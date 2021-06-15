from logging import getLogger

from django import forms
from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import (IS_POPUP_VAR, TO_FIELD_VAR,
                                          csrf_protect_m)
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import PermissionDenied
from django.forms.formsets import all_valid
from django.urls import path
from django.utils.translation import gettext as _

from main.file_parser import parse_file
from main.models import (Crop, Device, LightSource, Phase, Region, Set,
                         SpectralData)

logger = getLogger(__name__)

admin.site.register(Crop)
admin.site.register(Phase)
admin.site.register(Device)
admin.site.register(Region)
admin.site.register(LightSource)
admin.site.register(Set)


class ImportForm(forms.Form):
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True})
    )
    crop = forms.ModelChoiceField(Crop.objects.all())
    region = forms.ModelChoiceField(Region.objects.all())
    device = forms.ModelChoiceField(Device.objects.all(), required=False)
    phase = forms.ModelChoiceField(Phase.objects.all(), required=False)
    set = forms.ModelChoiceField(Set.objects.all(), required=False)
    light_source = forms.ModelChoiceField(LightSource.objects.all(), required=False)
    registered_at = forms.DateTimeField(required=False, widget=AdminDateWidget)
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)

    class Meta:
        model = SpectralData


@admin.register(SpectralData)
class SpectralDataAdmin(admin.ModelAdmin):
    change_list_template = "spectral_data.html"
    list_display = ["__str__", "wavelength", "intensity", "crop", "region", "phase"]
    list_filter = ["crop", "region", "phase"]
    import_fields = [
        "crop",
        "region",
        "device",
        "phase",
        "set",
        "light_source",
        "registered_at",
        "latitude",
        "longitude",
        "file_field",
    ]

    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path("import-files/", self.import_files))
        return urls

    @csrf_protect_m
    def import_files(self, request, form_url=""):
        # with transaction.atomic(using=router.db_for_write(self.model)):
        return self._changeform_view_m(request, form_url=form_url)

    def _changeform_view_m(self, request, form_url):
        """Modified version of _chanfeform_view."""
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                "The field %s cannot be referenced." % to_field
            )

        model = self.model
        opts = model._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        fieldsets = [(None, {"fields": self.import_fields})]
        formsets, inline_instances = self._create_formsets(request, None, change=False)

        if request.method == "POST":
            form = ImportForm(request.POST, request.FILES)
            form_validated = form.is_valid()
            if all_valid(formsets) and form_validated:
                form.cleaned_data.pop("file_field")
                for f in form.files.getlist("file_field"):
                    with f.open() as fh:
                        try:
                            parse_file(fh.read(), **form.cleaned_data)
                        except Exception as exc:
                            logger.exception(f"Cant parse file {f}")
                            messages.warning(
                                request, _("File %s NOT imported: %s") % (f, exc)
                            )
                messages.success(request, _("Objects imported"))
        else:
            form = ImportForm()

        readonly_fields = self.get_readonly_fields(request)
        adminForm = helpers.AdminForm(
            form,
            list(fieldsets),
            # Clear prepopulated fields on a view-only form to avoid a crash.
            self.get_prepopulated_fields(request)
            if self.has_change_permission(request)
            else {},
            readonly_fields,
            model_admin=self,
        )
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        title = _("Import %s")
        context = {
            **self.admin_site.each_context(request),
            "title": title % opts.verbose_name,
            "subtitle": None,
            "adminform": adminForm,
            "object_id": None,
            "original": None,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": helpers.AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
            "show_save_and_continue": False,
            "show_save_and_add_another": False,
            "show_save_as_new": False,
        }

        return self.render_change_form(
            request, context, add=True, change=False, form_url=form_url
        )
