
/*  Config-Store Client API Usage Call Flow Web Sequence Diagram data
 *
 * The following can be pasted into Web Sequence Diagram tool here:
 *   https://www.websequencediagrams.com/
 * This will generate a picture of the typicall call flow between a Config-Store
 * Client and the Config-Store API.


--- CUT_HERE-----------------------------------------------------------------------
title Config-Store Client API Usage Call Flow

cfstore_Client->Config-Store: cfstore_open_ctx(security_key_prefix)
Config-Store->cfstore_Client: returns hOwner

note left of cfstore_Client: Client find
cfstore_Client->Config-Store: cfstore_handle cfstore_find(cfstore_handle owner, const char* key_name_query, cfstore_handle previous=NULL)
Config-Store->cfstore_Client: returns key_handle to matching key_name

note left of cfstore_Client: Client uses key_handle as prev argument
cfstore_Client->Config-Store: cfstore_handle cfstore_find(cfstore_handle owner, const char* key_name_query, cfstore_handle previous=key_handle)
Config-Store->cfstore_Client: returns key handle to matching key_name

note over cfstore_Client,Config-Store: client iterates to get complete find list

note left of cfstore_Client: cfstore_Client create new object
cfstore_Client->Config-Store: cfstore_open(hOwner, key_name, valueL, kdesc with O_CREATE)
Config-Store->cfstore_Client: returns hObj

note left of cfstore_Client: cfstore_Client performs operations if required

note left of cfstore_Client: cfstore_Client close new object hObj
cfstore_Client->Config-Store: cfstore_close(hObj)
Config-Store->cfstore_Client: OK


note left of cfstore_Client: cfstore_Client opens pre-existing object
cfstore_Client->Config-Store: cfstore_open(hOwner, key_name, NULL, NULL)
Config-Store->cfstore_Client: returns hObj

note left of cfstore_Client: cfstore_Client seeks in pre-existing object
cfstore_Client->Config-Store: cfstore_rseek(hObj, ... )
Config-Store->cfstore_Client: returns data

note left of cfstore_Client: cfstore_Client reads pre-existing object
cfstore_Client->Config-Store: cfstore_read(hObj, ... )
Config-Store->cfstore_Client: returns data

note left of cfstore_Client: cfstore_Client closes pre-existing object
cfstore_Client->Config-Store: cfstore_close(hObj)
Config-Store->cfstore_Client: OK


note left of cfstore_Client: cfstore_Client closes security context with Config-Store
cfstore_Client->Config-Store: cfstore_close_ctx(hOwner)
Config-Store->cfstore_Client: OK
--- CUT_HERE-----------------------------------------------------------------------

*/


