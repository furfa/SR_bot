from django.forms.models import model_to_dict


class DjangoModelAutoStr(object):

    def __str__(self):
        d = model_to_dict(self, fields=[field.name for field in self._meta.fields])
        attrib_str = ", ".join(f"{k}='{v}'" for k, v in list(d.items())[:5])
        return str(type(self).__name__) + "(" + attrib_str + ")"