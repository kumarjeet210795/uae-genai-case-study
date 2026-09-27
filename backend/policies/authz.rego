package enterprise.authz

import future.keywords.or

default allow := false

# Reads are allowed only for users belonging to the relevant department,
# or for admins. This is a demo policy; production should use resource ACLs.
allow if {
    input.action == "read"
    input.resource == "get_invoice_status"
    ("finance" in input.user.groups) or ("admins" in input.user.groups)
}

allow if {
    input.action == "read"
    input.resource == "get_it_case_status"
    ("it" in input.user.groups) or ("admins" in input.user.groups)
}

allow if {
    input.action == "read"
    input.resource == "get_d365_case"
    ("employees" in input.user.groups) or ("admins" in input.user.groups)
}

allow if {
    input.action == "write"
    input.resource == "create_it_request"
    ("it" in input.user.groups) or ("admins" in input.user.groups)
}

# Purchase writes are intentionally denied to the tool layer in this demo.
# The application creates an approval request first.
allow if {
    input.action == "write"
    input.resource == "create_purchase_request"
    ("procurement" in input.user.groups) or ("admins" in input.user.groups)
}

