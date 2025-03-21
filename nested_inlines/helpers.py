import django.contrib.admin.helpers
from django.contrib.admin.helpers import InlineAdminFormSet

class AdminErrorList(django.contrib.admin.helpers.AdminErrorList):
    """
    Stores all errors for the form/formsets in an add/change stage view.
    """
    def __init__(self, form, inline_formsets):
        super(AdminErrorList, self).__init__(form, inline_formsets)

        if form.is_bound:
            self.extend(form.errors.values())
            for inline_formset in inline_formsets:
                self._add_formset_recursive(inline_formset)

    def _add_formset_recursive(self, formset):
        #check if it is a wrapped formset
        if isinstance(formset, InlineAdminFormSet):
            formset = formset.formset

        self.extend(formset.non_form_errors())
        for errors_in_inline_form in formset.errors:
            self.extend(list(errors_in_inline_form.values()))

        #support for nested formsets
        for form in formset:
            if hasattr(form, 'nested_formsets'):
                for fs in form.nested_formsets:
                    self._add_formset_recursive(fs)
