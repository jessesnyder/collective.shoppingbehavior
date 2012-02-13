collective.shoppingbehavior
=============================

This document contains design notes for the ``collective.shoppingbehavior``
package.

Introduction
------------

This documentation is intended to be a starting point to get a quick sense of
how the package is constructed. A lot of information can be gleaned from the
source itself, in particular:

- the ``tests`` package
- the ``interfaces`` module
- docstrings throughout the code


What it does (preliminary sketch)
---------------------------------

The goal is to provide optional price assignment on dexterity content, similar
to the functionality of "PloneGetPaid".

A locally-assignable behavior, ``IPriced``, provides the schema extension, and
is locally enableable via the "actions" menu.

The presense of this menu option is determined by whether or not the context
object provides the IPotentiallyPriced interface. Currently this interface is
added to types which want to support pricing either via zcml or ``implements``
declarations in the type definition. This could be made configurable TTW by
adding a second behavior that did nothing but apply this marker interface.
