from __future__ import unicode_literals

from polymorphic.admin import StackedPolymorphicInline

from waves.models.inputs import *
from waves.admin.submissions import *


class OrganizeInputInline(StackedPolymorphicInline):
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

    class TextFieldInline(StackedPolymorphicInline.Child):
        model = TextParam

    class DecimalFieldInline(StackedPolymorphicInline.Child):
        model = DecimalParam

    class ListFieldInline(StackedPolymorphicInline.Child):
        model = ListParam

    model = AParam
    child_inlines = (
        FileInputInline,
        DecimalFieldInline,
        IntegerFieldInline,
        BooleanFielInline,
        ListFieldInline,
        TextFieldInline
    )
