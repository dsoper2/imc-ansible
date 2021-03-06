#!/usr/bin/python

DOCUMENTATION = '''
---
module: cisco_imc_ldap
short_description: Configure LDAP on a Cisco IMC server.
version_added: "0.9.0.0"
description:
  - TODO
options:
  TODO

requirements: ['imcsdk']
author: "Vikrant Balyan(vvb@cisco.com)"
'''

EXAMPLES = '''
TODO
'''


def login(module):
    ansible = module.params
    server = ansible.get('server')
    if server:
        return server

    from imcsdk.imchandle import ImcHandle
    results = {}
    try:
        server = ImcHandle(ip=ansible["ip"],
                           username=ansible["username"],
                           password=ansible["password"],
                           port=ansible["port"],
                           secure=ansible["secure"],
                           proxy=ansible["proxy"])
        server.login()
    except Exception as e:
        results["msg"] = str(e)
        module.fail_json(**results)
    return server


def logout(module, imc_server):
    ansible = module.params
    server = ansible.get('server')
    if server:
        # we used a pre-existing handle from another task.
        # do not logout
        return False

    if imc_server:
        imc_server.logout()
        return True
    return False


def setup(server, module):
    from imcsdk.apis.admin.ldap import ldap_configure
    from imcsdk.apis.admin.ldap import ldap_settings_exist

    results = {}
    err = False

    try:
        ansible = module.params

        args = {}
        for key in ansible:
            if key == 'state' or ansible.get(key) is None:
                continue
            args[key] = ansible.get(key)

        if ansible['state'] == 'present':
            exists, mo = ldap_settings_exist(handle=server,
                                             enabled=True,
                                             **args)
            if module.check_mode or exists:
                results["changed"] = not exists
                return results, False

            ldap_configure(handle=server, enabled=True, **args)
        elif ansible['state'] == 'absent':
            exists, mo = ldap_settings_exist(handle=server, enabled=False)
            if module.check_mode or exists:
                results["changed"] = not exists
                return results, False

            ldap_configure(handle=server, enabled=False)

        results['changed'] = True

    except Exception as e:
        err = True
        results["msg"] = str(e)
        results["changed"] = False

    return results, err


def main():
    from ansible.module_utils.basic import AnsibleModule
    from ansible.module_utils.cisco_imc import ImcConnection
    module = AnsibleModule(
        argument_spec=dict(
            basedn=dict(required=False),
            domain=dict(required=False),
            encryption=dict(required=False, default=True, type='bool'),
            timeout=dict(required=False, default=60, type='int'),
            user_search_precedence=dict(required=False),
            bind_method=dict(required=False, default='login-credentials', type='str'),
            bind_dn=dict(required=False),
            ldap_password=dict(required=False),
            filter=dict(required=False, type='str'),
            attribute=dict(required=False, type='str'),
            group_attribute=dict(required=False, type='str'),
            group_nested_search=dict(required=False, type='str'),
            group_auth=dict(required=False, default=False, type='bool'),
            ldap_servers=dict(required=False, type='list'),
            locate_directory_using_dns=dict(required=False, default=False, type='bool'),
            dns_domain_source=dict(required=False, default='extracted-domain', type='str'),
            dns_search_domain=dict(required=False),
            dns_search_forest=dict(required=False),

            state=dict(required=True,
                       choices=['present', 'absent'], type='str'),

            # ImcHandle
            server=dict(required=False, type='dict'),

            # Imc server credentials
            ip=dict(required=False, type='str'),
            username=dict(required=False, default="admin", type='str'),
            password=dict(required=False, type='str', no_log=True),
            port=dict(required=False, default=None),
            secure=dict(required=False, default=None),
            proxy=dict(required=False, default=None)
        ),
        supports_check_mode=True
    )

    conn = ImcConnection(module)
    server = conn.login()
    results, err = setup(server, module)
    conn.logout()
    if err:
        module.fail_json(**results)
    module.exit_json(**results)


if __name__ == '__main__':
    main()
