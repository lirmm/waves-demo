from __future__ import unicode_literals

from polymorphic.admin import PolymorphicInlineSupportMixin, StackedPolymorphicInline

from waves.admin.adaptors import SubmissionRunnerParamInLine
from waves.admin.base import DynamicInlinesAdmin
from waves.admin.submissions import *


class InputInline(StackedPolymorphicInline):
    """
    An inline for a polymorphic model.
    The actual form appearance of each row is determined by
    the child inline that corresponds with the actual model type.
    """

    class FileInputInline(StackedPolymorphicInline.Child):
        model = FileInput

    class IntegerFieldInline(StackedPolymorphicInline.Child):
        model = IntegerParam

    class BooleanFielInline(StackedPolymorphicInline.Child):
        model = BooleanParam

    model = AParam
    child_inlines = (
        FileInputInline,
        IntegerFieldInline,
        BooleanFielInline,
    )


@admin.register(Submission)
class SubmissionAdmin(PolymorphicInlineSupportMixin, WavesModelAdmin, DynamicInlinesAdmin):
    """
    Admin for orders.
    The inline is polymorphic.
    To make sure the inlines are properly handled,
    the ``PolymorphicInlineSupportMixin`` is needed to
    """
    inlines = (InputInline,)

    def get_inlines(self, request, obj=None):
        _inlines = [
            OrganizeInputInline,
            # OrgRepeatGroupInline,
            SubmissionOutputInline,
            ExitCodeInline,
        ]
        self.inlines = _inlines
        if obj.runner is not None and obj.runner.adaptor_params.filter(prevent_override=False).count() > 0:
            self.inlines.append(SubmissionRunnerParamInLine)
        return self.inlines
