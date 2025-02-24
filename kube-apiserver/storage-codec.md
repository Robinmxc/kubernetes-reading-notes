k8s资源在ETCD是怎么存储的
===============================
## 背景

之前在开发operator的时候，针对大规模CRD有对apiserver做一些定制化的开发，在数据存储到etcd之前做了一次压缩，下面我们来分析一下实现的整体流程，需要在哪个环节去做这个事情。这里面主要是分析出下面两个问题

* 问题1:  资源存储到etcd中是什么数据格式的
* 问题2: 怎么实现资源的解压缩

只要分析清楚这个两个问题，那么实现数据的解压缩就很容易了。

## Run方法

进程的入口，他会先初始化程序运行的各种配置。

```go
// Run runs the specified APIServer.  This should never exit.
func Run(ctx context.Context, opts options.CompletedOptions) error {
	// To help debugging, immediately log version
	klog.Infof("Version: %+v", utilversion.Get())

	klog.InfoS("Golang settings", "GOGC", os.Getenv("GOGC"), "GOMAXPROCS", os.Getenv("GOMAXPROCS"), "GOTRACEBACK", os.Getenv("GOTRACEBACK"))
	
	// 生成配置，opts是启动参数的各种配置，包含内部默认的以及外部传入的
	config, err := NewConfig(opts)
	if err != nil {
		return err
	}
	
	// 创建apiserver需要各种资源
	completed, err := config.Complete()
	if err != nil {
		return err
	}
	server, err := CreateServerChain(completed)
	if err != nil {
		return err
	}

	prepared, err := server.PrepareRun()
	if err != nil { 
		return err
	}

	return prepared.Run(ctx)
}
```

## NewConfig创建相关资源
这里面涉及到3个server的配置KubeAPIs ApiExtensions Aggregator，其中KubeAPIs代表内置的核心资源配置（deployment、pod、service这些），ApiExtensions代表扩展资源（自定义crd这些），最开始的BuildGenericConfig会返回storageFactory，storageFactory中就带有etcd存储数据用的各种初始化配置，这个是一个通用的配置。
```go
// NewConfig creates all the resources for running kube-apiserver, but runs none of them.
func NewConfig(opts options.CompletedOptions) (*Config, error) {
	c := &Config{
		Options: opts,
	}
  
	genericConfig, versionedInformers, storageFactory, err := controlplaneapiserver.BuildGenericConfig(
		opts.CompletedOptions,
		[]*runtime.Scheme{legacyscheme.Scheme, apiextensionsapiserver.Scheme, aggregatorscheme.Scheme},
		controlplane.DefaultAPIResourceConfigSource(),
		generatedopenapi.GetOpenAPIDefinitions,
	)
	if err != nil {
		return nil, err
	}

	kubeAPIs, serviceResolver, pluginInitializer, err := CreateKubeAPIServerConfig(opts, genericConfig, versionedInformers, storageFactory)
	if err != nil {
		return nil, err
	}
	c.KubeAPIs = kubeAPIs

	apiExtensions, err := controlplaneapiserver.CreateAPIExtensionsConfig(*kubeAPIs.ControlPlane.Generic, kubeAPIs.ControlPlane.VersionedInformers, pluginInitializer, opts.CompletedOptions, opts.MasterCount,
		serviceResolver, webhook.NewDefaultAuthenticationInfoResolverWrapper(kubeAPIs.ControlPlane.ProxyTransport, kubeAPIs.ControlPlane.Generic.EgressSelector, kubeAPIs.ControlPlane.Generic.LoopbackClientConfig, kubeAPIs.ControlPlane.Generic.TracerProvider))
	if err != nil {
		return nil, err
	}
	c.ApiExtensions = apiExtensions

	aggregator, err := controlplaneapiserver.CreateAggregatorConfig(*kubeAPIs.ControlPlane.Generic, opts.CompletedOptions, kubeAPIs.ControlPlane.VersionedInformers, serviceResolver, kubeAPIs.ControlPlane.ProxyTransport, kubeAPIs.ControlPlane.Extra.PeerProxy, pluginInitializer)
	if err != nil {
		return nil, err
	}
	c.Aggregator = aggregator

	return c, nil
}
```

## BuildGenericConfig生成公共配置
生成的genericapiserver.Config可以给多个server用，方法会返回一个storageFactory对象，storageFactory这里面就会生成存储etcd的相关配置，这里面有非常关键的一项就是，就是DefaultStorageMediaType，它指定来k8s资源存储到etcd中用的Codec（json、yaml、protobuf序列化方法）。

行处生成storageFactory对象，会先初始化一个默认配置StorageFactoryConfig，而它又会使用默认Serializer方法（legacyscheme.Codecs），间接调用的是serializer.NewCodecFactory(Scheme)方法，而这个函数会生成三种序列化方法：（jsonSerializer、yamlSerializer、protoSerializer），默认采用的是jsonSerializer，但是同时也会把支持的三种方式保存在accepts数组里，在调用SupportedMediaTypes方法中返回。

再往下会执行storageFactoryConfig.Complete(s.Etcd).New()方法
```go
// 函数接收通用控制平面 API 服务器的配置选项，并生成与之关联的 genericapiserver.Config。
// genericapiserver.Config 通常会在多个委托的 apiservers之间共享。
func BuildGenericConfig(
	s options.CompletedOptions,
	schemes []*runtime.Scheme,
	resourceConfig *serverstorage.ResourceConfig,
	getOpenAPIDefinitions func(ref openapicommon.ReferenceCallback) map[string]openapicommon.OpenAPIDefinition,
) (
	genericConfig *genericapiserver.Config,
	versionedInformers clientgoinformers.SharedInformerFactory,
	storageFactory *serverstorage.DefaultStorageFactory,
	lastErr error,
) {
	genericConfig = genericapiserver.NewConfig(legacyscheme.Codecs)
	genericConfig.Flagz = s.Flagz
	genericConfig.MergedResourceConfig = resourceConfig

	if lastErr = s.GenericServerRunOptions.ApplyTo(genericConfig); lastErr != nil {
		return
	}

	if lastErr = s.SecureServing.ApplyTo(&genericConfig.SecureServing, &genericConfig.LoopbackClientConfig); lastErr != nil {
		return
	}

	// Use protobufs for self-communication.
	// Since not every generic apiserver has to support protobufs, we
	// cannot default to it in generic apiserver and need to explicitly
	// set it in kube-apiserver.
	genericConfig.LoopbackClientConfig.ContentConfig.ContentType = "application/vnd.kubernetes.protobuf"
	// Disable compression for self-communication, since we are going to be
	// on a fast local network
	genericConfig.LoopbackClientConfig.DisableCompression = true

	kubeClientConfig := genericConfig.LoopbackClientConfig
	clientgoExternalClient, err := clientgoclientset.NewForConfig(kubeClientConfig)
	if err != nil {
		lastErr = fmt.Errorf("failed to create real external clientset: %w", err)
		return
	}
	trim := func(obj interface{}) (interface{}, error) {
		if accessor, err := meta.Accessor(obj); err == nil && accessor.GetManagedFields() != nil {
			accessor.SetManagedFields(nil)
		}
		return obj, nil
	}
	versionedInformers = clientgoinformers.NewSharedInformerFactoryWithOptions(clientgoExternalClient, 10*time.Minute, clientgoinformers.WithTransform(trim))

	if lastErr = s.Features.ApplyTo(genericConfig, clientgoExternalClient, versionedInformers); lastErr != nil {
		return
	}
	if lastErr = s.APIEnablement.ApplyTo(genericConfig, resourceConfig, legacyscheme.Scheme); lastErr != nil {
		return
	}
	if lastErr = s.EgressSelector.ApplyTo(genericConfig); lastErr != nil {
		return
	}
	if utilfeature.DefaultFeatureGate.Enabled(genericfeatures.APIServerTracing) {
		if lastErr = s.Traces.ApplyTo(genericConfig.EgressSelector, genericConfig); lastErr != nil {
			return
		}
	}
	// wrap the definitions to revert any changes from disabled features
	getOpenAPIDefinitions = openapi.GetOpenAPIDefinitionsWithoutDisabledFeatures(getOpenAPIDefinitions)
	namer := openapinamer.NewDefinitionNamer(schemes...)
	genericConfig.OpenAPIConfig = genericapiserver.DefaultOpenAPIConfig(getOpenAPIDefinitions, namer)
	genericConfig.OpenAPIConfig.Info.Title = "Kubernetes"
	genericConfig.OpenAPIV3Config = genericapiserver.DefaultOpenAPIV3Config(getOpenAPIDefinitions, namer)
	genericConfig.OpenAPIV3Config.Info.Title = "Kubernetes"

	genericConfig.LongRunningFunc = filters.BasicLongRunningRequestCheck(
		sets.NewString("watch", "proxy"),
		sets.NewString("attach", "exec", "proxy", "log", "portforward"),
	)

	if genericConfig.EgressSelector != nil {
		s.Etcd.StorageConfig.Transport.EgressLookup = genericConfig.EgressSelector.Lookup
	}
	if utilfeature.DefaultFeatureGate.Enabled(genericfeatures.APIServerTracing) {
		s.Etcd.StorageConfig.Transport.TracerProvider = genericConfig.TracerProvider
	} else {
		s.Etcd.StorageConfig.Transport.TracerProvider = noopoteltrace.NewTracerProvider()
	}

	storageFactoryConfig := kubeapiserver.NewStorageFactoryConfig()
	storageFactoryConfig.CurrentVersion = genericConfig.EffectiveVersion
	storageFactoryConfig.APIResourceConfig = genericConfig.MergedResourceConfig
	storageFactoryConfig.DefaultResourceEncoding.SetEffectiveVersion(genericConfig.EffectiveVersion)
	// 覆盖DefaultStorageMediaType类型从json变成protobuf
  storageFactory, lastErr = storageFactoryConfig.Complete(s.Etcd).New()
	if lastErr != nil {
		return
	}
	// storageFactory.StorageConfig is copied from etcdOptions.StorageConfig,
	// the StorageObjectCountTracker is still nil. Here we copy from genericConfig.
	storageFactory.StorageConfig.StorageObjectCountTracker = genericConfig.StorageObjectCountTracker
	// 这个地方会通过genericConfig的配置，生成Transformers方法
	if lastErr = s.Etcd.ApplyWithStorageFactoryTo(storageFactory, genericConfig); lastErr != nil {
		return
	}

	ctx := wait.ContextForChannel(genericConfig.DrainedNotify())

	// Authentication.ApplyTo requires already applied OpenAPIConfig and EgressSelector if present
	if lastErr = s.Authentication.ApplyTo(ctx, &genericConfig.Authentication, genericConfig.SecureServing, genericConfig.EgressSelector, genericConfig.OpenAPIConfig, genericConfig.OpenAPIV3Config, clientgoExternalClient, versionedInformers, genericConfig.APIServerID); lastErr != nil {
		return
	}

	var enablesRBAC bool
	genericConfig.Authorization.Authorizer, genericConfig.RuleResolver, enablesRBAC, err = BuildAuthorizer(
		ctx,
		s,
		genericConfig.EgressSelector,
		genericConfig.APIServerID,
		versionedInformers,
	)
	if err != nil {
		lastErr = fmt.Errorf("invalid authorization config: %w", err)
		return
	}
	if s.Authorization != nil && !enablesRBAC {
		genericConfig.DisabledPostStartHooks.Insert(rbacrest.PostStartHookName)
	}

	lastErr = s.Audit.ApplyTo(genericConfig)
	if lastErr != nil {
		return
	}

	if utilfeature.DefaultFeatureGate.Enabled(genericfeatures.AggregatedDiscoveryEndpoint) {
		genericConfig.AggregatedDiscoveryGroupManager = aggregated.NewResourceManager("apis")
	}

	return
}
```

### Complete 方法覆盖配置

这个Complete方法非常关键，他会覆盖上面提到默认序列化类型，覆盖的数据来自s.Etcd.DefaultStorageMediaType，这个数据就来自下面的NewOptions里的配置，初始化成了protobuf类型。看到这里逻辑已经很清楚了，虽然默认是json，但是后续会被修改成protobuf。

```go
// Complete completes the StorageFactoryConfig with provided etcdOptions returning completedStorageFactoryConfig.
// This method mutates the receiver (StorageFactoryConfig).  It must never mutate the inputs.
func (c *StorageFactoryConfig) Complete(etcdOptions *serveroptions.EtcdOptions) *completedStorageFactoryConfig {
	c.StorageConfig = etcdOptions.StorageConfig
	c.DefaultStorageMediaType = etcdOptions.DefaultStorageMediaType
	c.EtcdServersOverrides = etcdOptions.EtcdServersOverrides
	return &completedStorageFactoryConfig{c}
}
```

### NewOptions 配置

在执行Run之前，有一个步骤是Options的配置环节 s := options.NewServerRunOptions()，这个环节里面就有关于etcd部分的options配置，可以看到，DefaultStorageMediaType默认被设置成了protobuf。

```go
// NewOptions creates a new ServerRunOptions object with default parameters
func NewOptions() *Options {
    s := Options{
        GenericServerRunOptions: genericoptions.NewServerRunOptions(),
        Etcd:                    genericoptions.NewEtcdOptions(storagebackend.NewDefaultConfig(kubeoptions.DefaultEtcdPathPrefix, nil)),
        SecureServing:           kubeoptions.NewSecureServingOptions(),
        Audit:                   genericoptions.NewAuditOptions(),
        Features:                genericoptions.NewFeatureOptions(),
        Admission:               kubeoptions.NewAdmissionOptions(),
        Authentication:          kubeoptions.NewBuiltInAuthenticationOptions().WithAll(),
        Authorization:           kubeoptions.NewBuiltInAuthorizationOptions(),
        APIEnablement:           genericoptions.NewAPIEnablementOptions(),
        EgressSelector:          genericoptions.NewEgressSelectorOptions(),
        Metrics:                 metrics.NewOptions(),
        Logs:                    logs.NewOptions(),
        Traces:                  genericoptions.NewTracingOptions(),

        EnableLogsHandler:                   false,
        EventTTL:                            1 * time.Hour,
        AggregatorRejectForwardingRedirects: true,
        SystemNamespaces:                    []string{metav1.NamespaceSystem, metav1.NamespacePublic, metav1.NamespaceDefault},
    }

    // Overwrite the default for storage data format.
    s.Etcd.DefaultStorageMediaType = "application/vnd.kubernetes.protobuf"

    return &s
}
```

## KubeAPIs生成分析
回到上面NewConfig方法，这里面会生成一个调用CreateKubeAPIServerConfig，生成通用控制平面的配置*controlplane.Config

### CreateKubeAPIServerConfig分析
这个方法又会调用controlplaneapiserver.CreateConfig方法，这个方法会传入storageFactory，就是上面分析出来的protobuf类型的存储方法。这个对象被放入kubeAPIs的ControlPlane.Extra.StorageFactory。
```go
// CreateKubeAPIServerConfig creates all the resources for running the API server, but runs none of them
func CreateKubeAPIServerConfig(
	opts options.CompletedOptions,
	genericConfig *genericapiserver.Config,
	versionedInformers clientgoinformers.SharedInformerFactory,
	storageFactory *serverstorage.DefaultStorageFactory,
) (
	*controlplane.Config,
	aggregatorapiserver.ServiceResolver,
	[]admission.PluginInitializer,
	error,
) {
	// global stuff
	capabilities.Setup(opts.AllowPrivileged, opts.MaxConnectionBytesPerSec)

	// additional admission initializers
	kubeAdmissionConfig := &kubeapiserveradmission.Config{
		CloudConfigFile: opts.CloudProvider.CloudConfigFile,
	}
	kubeInitializers, err := kubeAdmissionConfig.New()
	if err != nil {
		return nil, nil, nil, fmt.Errorf("failed to create admission plugin initializer: %w", err)
	}

	serviceResolver := buildServiceResolver(opts.EnableAggregatorRouting, genericConfig.LoopbackClientConfig.Host, versionedInformers)
	controlplaneConfig, admissionInitializers, err := controlplaneapiserver.CreateConfig(opts.CompletedOptions, genericConfig, versionedInformers, storageFactory, serviceResolver, kubeInitializers)
	if err != nil {
		return nil, nil, nil, err
	}

	config := &controlplane.Config{
		ControlPlane: *controlplaneConfig,
		Extra: controlplane.Extra{
			KubeletClientConfig: opts.KubeletConfig,

			ServiceIPRange:          opts.PrimaryServiceClusterIPRange,
			APIServerServiceIP:      opts.APIServerServiceIP,
			SecondaryServiceIPRange: opts.SecondaryServiceClusterIPRange,

			APIServerServicePort: 443,

			ServiceNodePortRange:      opts.ServiceNodePortRange,
			KubernetesServiceNodePort: opts.KubernetesServiceNodePort,

			EndpointReconcilerType: reconcilers.Type(opts.EndpointReconcilerType),
			MasterCount:            opts.MasterCount,
		},
	}

	if config.ControlPlane.Generic.EgressSelector != nil {
		// Use the config.ControlPlane.Generic.EgressSelector lookup to find the dialer to connect to the kubelet
		config.Extra.KubeletClientConfig.Lookup = config.ControlPlane.Generic.EgressSelector.Lookup

		// Use the config.ControlPlane.Generic.EgressSelector lookup as the transport used by the "proxy" subresources.
		networkContext := egressselector.Cluster.AsNetworkContext()
		dialer, err := config.ControlPlane.Generic.EgressSelector.Lookup(networkContext)
		if err != nil {
			return nil, nil, nil, err
		}
		c := config.ControlPlane.Extra.ProxyTransport.Clone()
		c.DialContext = dialer
		config.ControlPlane.ProxyTransport = c
	}

	return config, serviceResolver, admissionInitializers, nil
}
```

## ApiExtensions生成分析
回到上面NewConfig方法，这里面会生成一个调用CreateAPIExtensionsConfig方法，生成一个扩展资源的配置apiextensionsConfig

### CreateAPIExtensionsConfig分析
通过源码分析可以知道apiextensionsConfig拷贝自kubeAPIServerConfig，但是没有使用它上面的RESTOptionsGetter方法，而是自己生成了一个默认的Codec，然后覆盖上面的RESTOptionsGetter方法，另外还生成了一个CRDRESTOptionsGetter方法，可以看到不管是RESTOptionsGetter还是CRDRESTOptionsGetter，这里面使用的序列化方式都是默认的json方式。
```go
func CreateAPIExtensionsConfig(
	kubeAPIServerConfig server.Config,
	kubeInformers informers.SharedInformerFactory,
	pluginInitializers []admission.PluginInitializer,
	commandOptions options.CompletedOptions,
	masterCount int,
	serviceResolver webhook.ServiceResolver,
	authResolverWrapper webhook.AuthenticationInfoResolverWrapper,
) (*apiextensionsapiserver.Config, error) {
	// make a shallow copy to let us twiddle a few things
	// most of the config actually remains the same.  We only need to mess with a couple items related to the particulars of the apiextensions
	genericConfig := kubeAPIServerConfig
	genericConfig.PostStartHooks = map[string]server.PostStartHookConfigEntry{}
	genericConfig.RESTOptionsGetter = nil

	// copy the etcd options so we don't mutate originals.
	// we assume that the etcd options have been completed already.  avoid messing with anything outside
	// of changes to StorageConfig as that may lead to unexpected behavior when the options are applied.
	etcdOptions := *commandOptions.Etcd
	// this is where the true decodable levels come from.
	etcdOptions.StorageConfig.Codec = apiextensionsapiserver.Codecs.LegacyCodec(v1beta1.SchemeGroupVersion, v1.SchemeGroupVersion)
	// prefer the more compact serialization (v1beta1) for storage until https://issue.k8s.io/82292 is resolved for objects whose v1 serialization is too big but whose v1beta1 serialization can be stored
	etcdOptions.StorageConfig.EncodeVersioner = runtime.NewMultiGroupVersioner(v1beta1.SchemeGroupVersion, schema.GroupKind{Group: v1beta1.GroupName})
	etcdOptions.SkipHealthEndpoints = true // avoid double wiring of health checks
	if err := etcdOptions.ApplyTo(&genericConfig); err != nil {
		return nil, err
	}

	// override MergedResourceConfig with apiextensions defaults and registry
	if err := commandOptions.APIEnablement.ApplyTo(
		&genericConfig,
		apiextensionsapiserver.DefaultAPIResourceConfigSource(),
		apiextensionsapiserver.Scheme); err != nil {
		return nil, err
	}
	apiextensionsConfig := &apiextensionsapiserver.Config{
		GenericConfig: &server.RecommendedConfig{
			Config:                genericConfig,
			SharedInformerFactory: kubeInformers,
		},
		ExtraConfig: apiextensionsapiserver.ExtraConfig{
			CRDRESTOptionsGetter: apiextensionsoptions.NewCRDRESTOptionsGetter(etcdOptions, genericConfig.ResourceTransformers, genericConfig.StorageObjectCountTracker),
			MasterCount:          masterCount,
			AuthResolverWrapper:  authResolverWrapper,
			ServiceResolver:      serviceResolver,
		},
	}

	// we need to clear the poststarthooks so we don't add them multiple times to all the servers (that fails)
	apiextensionsConfig.GenericConfig.PostStartHooks = map[string]server.PostStartHookConfigEntry{}

	return apiextensionsConfig, nil
}
```

## Transformers生成
上面BuildGenericConfig中会调用s.Etcd.ApplyWithStorageFactoryTo(storageFactory, genericConfig)，初始化Transformers，这个Transformers的作用主要是加解密用，提供了TransformFromStorage和TransformToStorage两个方法，因此就像最开始提出，通过实现一个Transformers模块，在初始化的时候注入进去，就可以达到对写入etcd的资源做一次压缩，读取数据的时候解压缩。
```go
type Transformer interface {
	Read
	Write
}

type Read interface {
	// TransformFromStorage may transform the provided data from its underlying storage representation or return an error.
	// Stale is true if the object on disk is stale and a write to etcd should be issued, even if the contents of the object
	// have not changed.
	TransformFromStorage(ctx context.Context, data []byte, dataCtx Context) (out []byte, stale bool, err error)
}

type Write interface {
	// TransformToStorage may transform the provided data into the appropriate form in storage or return an error.
	TransformToStorage(ctx context.Context, data []byte, dataCtx Context) (out []byte, err error)
}
```

### ApplyWithStorageFactoryTo分析
这个方法很简单，就是调用maybeApplyResourceTransformers方法，加载加解密的配置文件，通过配置文件生成transform，保存到server.Config上（即c.ResourceTransformers），最后生成一个RESTOptionsGetter，保存在*server.Config里面（后面会说明怎么用RESTOptionsGetter）。

```go
// ApplyWithStorageFactoryTo mutates the provided server.Config.  It must never mutate the receiver (EtcdOptions).
func (s *EtcdOptions) ApplyWithStorageFactoryTo(factory serverstorage.StorageFactory, c *server.Config) error {
	if s == nil {
		return nil
	}

	if !s.SkipHealthEndpoints {
		if err := s.addEtcdHealthEndpoint(c); err != nil {
			return err
		}
	}

	// setup encryption
	if err := s.maybeApplyResourceTransformers(c); err != nil {
		return err
	}

	metrics.SetStorageMonitorGetter(monitorGetter(factory))

	c.RESTOptionsGetter = s.CreateRESTOptionsGetter(factory, c.ResourceTransformers)
	return nil
}
```

### maybeApplyResourceTransformers分析
这个方法包含几个步骤
1. 如果ResourceTransformers已经不为空，直接返回，不需要去做初始化了
2. 没有配置加解密文件（EncryptionProviderConfigFilepath为空），也直接返回
3.  读取配置的加解密文件文件，做transform的初始化用。

最终会把生成的transform赋值给*server.Config的ResourceTransformers
```go
func (s *EtcdOptions) maybeApplyResourceTransformers(c *server.Config) (err error) {
	// 如果已经不为空，直接返回，不需要去做初始化了
	if c.ResourceTransformers != nil {
		return nil
	}
	
	// 没有配置加解密，也直接返回
	if len(s.EncryptionProviderConfigFilepath) == 0 {
		return nil
	}

	ctxServer := wait.ContextForChannel(c.DrainedNotify())
	ctxTransformers, closeTransformers := context.WithCancel(ctxServer)
	defer func() {
		// in case of error, we want to close partially initialized (if any) transformers
		if err != nil {
			closeTransformers()
		}
	}()
	
	// 读取配置的文件，做transform的初始化用
	encryptionConfiguration, err := encryptionconfig.LoadEncryptionConfig(ctxTransformers, s.EncryptionProviderConfigFilepath, s.EncryptionProviderConfigAutomaticReload, c.APIServerID)
	if err != nil {
		return err
	}

	if s.EncryptionProviderConfigAutomaticReload {
		// with reload=true we will always have 1 health check
		if len(encryptionConfiguration.HealthChecks) != 1 {
			return fmt.Errorf("failed to start kms encryption config hot reload controller. only 1 health check should be available when reload is enabled")
		}

		// Here the dynamic transformers take ownership of the transformers and their cancellation.
		dynamicTransformers := encryptionconfig.NewDynamicTransformers(encryptionConfiguration.Transformers, encryptionConfiguration.HealthChecks[0], closeTransformers, encryptionConfiguration.KMSCloseGracePeriod)

		// add post start hook to start hot reload controller
		// adding this hook here will ensure that it gets configured exactly once
		err = c.AddPostStartHook(
			"start-encryption-provider-config-automatic-reload",
			func(_ server.PostStartHookContext) error {
				dynamicEncryptionConfigController := encryptionconfigcontroller.NewDynamicEncryptionConfiguration(
					"encryption-provider-config-automatic-reload-controller",
					s.EncryptionProviderConfigFilepath,
					dynamicTransformers,
					encryptionConfiguration.EncryptionFileContentHash,
					c.APIServerID,
				)

				go dynamicEncryptionConfigController.Run(ctxServer)

				return nil
			},
		)
		if err != nil {
			return fmt.Errorf("failed to add post start hook for kms encryption config hot reload controller: %w", err)
		}

		c.ResourceTransformers = dynamicTransformers
		if !s.SkipHealthEndpoints {
			addHealthChecksWithoutLivez(c, dynamicTransformers)
		}
	} else {
		c.ResourceTransformers = encryptionconfig.StaticTransformers(encryptionConfiguration.Transformers)
		if !s.SkipHealthEndpoints {
			addHealthChecksWithoutLivez(c, encryptionConfiguration.HealthChecks...)
		}
	}

	return nil
}
```

### CreateRESTOptionsGetter分析
上面ApplyWithStorageFactoryTo步骤的最后，会执行CreateRESTOptionsGetter方法，生成一个transformerStorageFactory对象，这个对象实现了接口serverstorage.StorageFactory的方法，并且集成了Transformer，通过实现NewConfig方法，可以把transformerStorageFactory中的resourceTransformers设置到config上，这样后续调用NewConfig方法，就会自动把上面配置好的Transformer都设置上去。从而在其他模块调用的时候，Transformer配置能生效。
```go
// transformerStorageFactory是对StorageFactory的封装
var _ serverstorage.StorageFactory = &transformerStorageFactory{}

type transformerStorageFactory struct {
	delegate             serverstorage.StorageFactory
	resourceTransformers storagevalue.ResourceTransformers
}

func (t *transformerStorageFactory) NewConfig(resource schema.GroupResource, example runtime.Object) (*storagebackend.ConfigForResource, error) {
	config, err := t.delegate.NewConfig(resource, example)
	if err != nil {
		return nil, err
	}

	configCopy := *config
	resourceConfig := configCopy.Config
	resourceConfig.Transformer = t.resourceTransformers.TransformerForResource(resource)
	configCopy.Config = resourceConfig

	return &configCopy, nil
}

func (s *EtcdOptions) CreateRESTOptionsGetter(factory serverstorage.StorageFactory, resourceTransformers storagevalue.ResourceTransformers) generic.RESTOptionsGetter {
	if resourceTransformers != nil {
		factory = &transformerStorageFactory{
			delegate:             factory,
			resourceTransformers: resourceTransformers,
		}
	}
	return &StorageFactoryRestOptionsFactory{Options: *s, StorageFactory: factory}
}
```

## 自定义Transformer实现
通过上面的分析，如果需要自定义Transformer，就需要在maybeApplyResourceTransformers方法之前，自己实现一个Transformer插件，这样在就不会走到maybeApplyResourceTransformers里面的读取文件，生成插件的逻辑。

## 总结
通过上面的源码分析，最开始的两个问题答案就出来了

问题1:  资源存储到etcd中是什么数据格式的 
* k8s默认资源，也就是通过generic config生成的KubeAPIServerConfig，使用的是protobuf方式序列化 
* crd资源，使用的是默认的json方式序列化

问题2: 怎么实现资源的解压缩

自己实现一个Transformer插件，然后通过覆盖genericConfig上的ResourceTransformers即可。
