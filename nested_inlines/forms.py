from django.forms.forms import BaseForm, ErrorDict
from django.forms.models import ModelForm, BaseInlineFormSet

class NestedFormMixin(object):
    def full_clean(self):
        """
        Cleans all of self.data and populates self._errors and
        self.cleaned_data.
        """
        self._errors = ErrorDict()
        if not self.is_bound: # Stop further processing.
            return
        self.cleaned_data = {}
        # If the form is permitted to be empty, and none of the form data has
        # changed from the initial data, short circuit any validation.
        if self.empty_permitted and not self.has_changed() and not self.dependency_has_changed():
            return
        self._clean_fields()
        self._clean_form()
        self._post_clean()

    def dependency_has_changed(self):
        """
        Returns true, if any dependent form has changed.
        This is needed to force validation, even if this form wasn't changed but a dependent form
        """
        return False

class BaseNestedForm(NestedFormMixin, BaseForm):
    pass

class NestedFormSetMixin(object):
    def save_new_objects(self, commit=True):
        # same as django's except in case when a form is not changed but the
        # instance itself is not saved yet, we are not skipping saving
        self.new_objects = []
        for form in self.extra_forms:
            if form.instance.pk and not form.has_changed():
                continue
            # If someone has marked an add form for deletion, don't save the
            # object.
            if self.can_delete and self._should_delete_form(form):
                continue

            if not form.cleaned_data:
                # its an empty form (shown as an extra) that has no errors
                continue

            self.new_objects.append(self.save_new(form, commit=commit))
            if not commit:
                self.saved_forms.append(form)
        return self.new_objects

    def dependency_has_changed(self):
        for form in self.forms:
            if form.has_changed() or form.dependency_has_changed():
                return True
        return False

class BaseNestedInlineFormSet(NestedFormSetMixin, BaseInlineFormSet):
    pass

class NestedModelFormMixin(NestedFormMixin):
    def dependency_has_changed(self):
        # check for the nested_formsets attribute, added by the admin app.
        # TODO this should be generalized
        if hasattr(self, 'nested_formsets'):
            for f in self.nested_formsets:
                if f.dependency_has_changed():
                    return True
        return False

class BaseNestedModelForm(NestedModelFormMixin, ModelForm):
    pass
