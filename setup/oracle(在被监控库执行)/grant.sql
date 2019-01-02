--对Oracle监控用户授权
--基本权限，心大的可以直接用dba角色
grant connect,resource to ...;
--查询数据字典权限
grant select any dictionary to ...;