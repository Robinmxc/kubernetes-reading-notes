#!/bin/bash
set -x
  function ldap_add_or_modify (){
    local LDIF_FILE=$1

    echo "Processing file ${LDIF_FILE}"
    if grep -iq changetype $LDIF_FILE ; then
        ( ldapmodify -Y EXTERNAL -Q -H ldapi:/// -f $LDIF_FILE 2>&1 || ldapmodify -h localhost -p 389 -D cn=admin,{{ LDAP.LDAP_BASE_DN }} -w "{{ LDAP.LDAP_ADMIN_PASSWORD }}" -f $LDIF_FILE 2>&1 ) | log-helper debug
    else
        ( ldapadd -Y EXTERNAL -Q -H ldapi:/// -f $LDIF_FILE 2>&1 || ldapadd -h localhost -p 389 -D cn=admin,{{ LDAP.LDAP_BASE_DN }} -w "{{ LDAP.LDAP_ADMIN_PASSWORD }}" -f $LDIF_FILE 2>&1 ) | log-helper debug
    fi
  }

for f in $(find {{ ldap_base_dir }}/schema/ -type f -name \*.ldif  | sort); do
          ldap_add_or_modify "$f"
done


#!/bin/bash
set -x
  function ldap_add_or_modify (){
    local LDIF_FILE=$1

    echo "Processing file ${LDIF_FILE}"
    if grep -iq changetype $LDIF_FILE ; then
        ( ldapmodify -Y EXTERNAL -Q -H ldapi:/// -f $LDIF_FILE 2>&1 || ldapmodify -h localhost -p 389 -D cn=admin,dc=ecnu,dc=edu,dc=cn -w "Shyfzx_163" -f $LDIF_FILE 2>&1 ) | log-helper debug
    else
        ( ldapadd -Y EXTERNAL -Q -H ldapi:/// -f $LDIF_FILE 2>&1 || ldapadd -h localhost -p 389 -D cn=admin,dc=ecnu,dc=edu,dc=cn -w "Shyfzx_163" -f $LDIF_FILE 2>&1 ) | log-helper debug
    fi
  }

for f in $(find /ruijie/ruijie-sourceid/openldap/schema/ -type f -name \*.ldif  | sort); do
          ldap_add_or_modify "$f"
done


Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/01_add_ppolicy.ldif
adding new entry "cn=module{0},cn=config"
ldap_add: Naming violation (64)

adding new entry "cn=module{0},cn=config"
ldap_add: Insufficient access (50)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/02_modify_ppolicy.ldif
modifying entry "cn=module{0},cn=config"

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/03_ppolicy_overlay.ldif
adding new entry "olcOverlay=ppolicy,olcDatabase={1}mdb,cn=config"

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/04_disable_anon.ldif
modifying entry "cn=config"
ldap_modify: Type or value exists (20)
        additional info: modify/add: olcDisallows: value #0 already exists

modifying entry "cn=config"
ldap_modify: Insufficient access (50)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/05_db-index.ldif
modifying entry "olcDatabase={1}mdb,cn=config"
ldap_modify: Type or value exists (20)
        additional info: modify/add: olcDbIndex: value #1 already exists

modifying entry "olcDatabase={1}mdb,cn=config"
ldap_modify: Insufficient access (50)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/06_limits.ldif
modifying entry "olcDatabase={1}mdb,cn=config"

modifying entry "olcDatabase={1}mdb,cn=config"
ldap_modify: Inappropriate matching (18)
        additional info: modify/add: olcDbMaxSize: no equality matching rule

modifying entry "olcDatabase={1}mdb,cn=config"
ldap_modify: Insufficient access (50)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/07_tls1.2.ldif
modifying entry "cn=config"

modifying entry "cn=config"
ldap_modify: Inappropriate matching (18)
        additional info: modify/add: olcTLSCipherSuite: no equality matching rule

modifying entry "cn=config"
ldap_modify: Insufficient access (50)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/08_name.ldif
adding new entry "dc=ecnu,dc=edu,dc=cn"
ldap_add: Already exists (68)

adding new entry "dc=ecnu,dc=edu,dc=cn"
ldap_add: Already exists (68)

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/09_olcAccess.ldif
modifying entry "olcDatabase={1}mdb,cn=config"

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/100_mod_syncprov.ldif
adding new entry "cn=module,cn=config"

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/101_syncprov.ldif
adding new entry "olcOverlay=syncprov,olcDatabase={1}mdb,cn=config"

Processing file /container/service/slapd/assets/config/bootstrap/ldif/custom/102_master_node.ldif
modifying entry "cn=config"

modifying entry "olcDatabase={1}mdb,cn=config"