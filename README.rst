==========
Casual CMS
==========

A CMS for Domain Driven Designer.

As a fan, this CMS is mostly inspired by Wagtail.
Casual CMS is based on domain modeling in pydantic, instead of Django
models. It does not requires to handle SQL migrations either.

TODO
----

* Page revision

* Page tags, and search by tags in jinja2

* Alembic SQL update

* Historic

* Display Errors in forms

* Tests error format in API

* Implement default site

* Ensure we can't delete a page if it is associated to a site

* Add widget to choose a snippet (browse snippet popup)

* Add widget to edit text using a wysiwyg

* Add widget to choose a page while doing page links (browse page popup)

* Define and implement errors on reserved word for page, snippet, and settings

* rename snippet slug by key

* Add tests for 422 errors

* Fix 401 Unauthorized (Not authenticated) / 403 Forbidden (Authenticated)

* Fix 500 errors when an invalid payload is posted on page/snippet/settings

* Open tickes for buggy feature with bool in react-jsonschema-form
