# upgrade-assist

This project is in it's early stages so use with care - it is useful though!

The aim of this project is to help identifying what to do when upgrading a war overlay project.

At present it only works with Alfresco however it should be fairly straightforward to make it work for any WAR overlay project.

## How to run

### Alfresco

The script upgrade-alfresco.sh controls the processing. You need to change three things:

* OLD - the version you are upgrading from
* NEW - the version you are upgrading to
* ../my-alfresco-extensions - the path to your customizations

## What it does

The shell script gets the Spring XML files from the old and the new version.

The python script extracts the bean definitions from your custom code and then looks to see if the same beans are defined in the base code.

If your bean overrides a base bean, and the base bean definition has changed then it will report a diff.

This is perhaps easiest to explain with an example.

If you want to restrict Site creation in Alfresco then you can do this by modifying the SiteService_security definition from public-services-security-context.xml.
The default definition for this bean changed between versions 4.2 and 5.0 (by adding org.alfresco.service.cmr.site.SiteService.isSiteAdmin=ACL_ALLOW), something that is easy to miss.

You get a nice report telling you what has changed, followed by the location of your custom definition and a diff between the old version and your custom definition

An example of the difference between 4.2.f and 5.0.d
```
BeanDef in all versions:SiteService_security
*** 
--- 
***************
*** 34,39 ****
--- 34,40 ----
                 org.alfresco.service.cmr.site.SiteService.setMembership=ACL_ALLOW
                 org.alfresco.service.cmr.site.SiteService.updateSite=ACL_ALLOW
                 org.alfresco.service.cmr.site.SiteService.countAuthoritiesWithRole=ACL_ALLOW
+                org.alfresco.service.cmr.site.SiteService.isSiteAdmin=ACL_ALLOW
                 org.alfresco.service.cmr.site.SiteService.*=ACL_DENY
              </value>
          </property>
Compared BeanDef in new version:alfresco/alfresco-open-mirror/4.2.f/repo/alfresco/public-services-security-context.xml
Compared BeanDef in old version:alfresco/alfresco-open-mirror/5.0.d/repo/alfresco/public-services-security-context.xml
```

## What could improve

 * Retrieval of the versioned code
 * The diff doesn't handle whitespace well.
 * XML namespaces - the bean namespace is defined in an inconsistent manner and it should be able to handle this better.
