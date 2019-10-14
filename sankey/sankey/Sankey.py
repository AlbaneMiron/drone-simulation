# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Sankey(Component):
    """A Sankey component.


Keyword arguments:
- id (string; optional): The ID of this component, used to identify dash components
in callbacks. The ID needs to be unique across all of the
components in an app.
- flows (dict; optional): A list of flows to display as arrows. flows has the following type: list of dicts containing keys 'fill', 'size', 'text'.
Those keys have the following types:
  - fill (string; optional)
  - size (number; required)
  - text (string; optional)"""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, flows=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'flows']
        self._type = 'Sankey'
        self._namespace = 'sankey'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'flows']
        self.available_wildcard_properties =            []

        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Sankey, self).__init__(**args)
