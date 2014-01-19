from django.db import models
class Frame(object):

    #TODO: Missing Validateion and exception raising
    def __init__(self, x, y, width, height):
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
    
    @staticmethod    
    def Parse(value):
    
        if value == '' or value is None:
            return Frame(0,0,0,0)
            
        (x, y, width, height) = value.split(',')
        return Frame(x, y, width, height)
        
    def __unicode__(self):
        return "%d,%d,%d,%d" % (self.x, self.y, self.width, self.height)
        

class FrameField(models.Field):

    __metaclass__ = models.SubfieldBase
    
     
    def __init__(self,  *args, **kwargs):
        #self.max_length = 68
        super(FrameField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'char(%s)' % 68
        
    def to_python(self, value):
        
        if isinstance(value, Frame):
            return value
            
        return Frame.Parse(value) 
        
    def get_prep_value(self, value):
        return self.to_python(value)
        
        
    def get_db_prep_save(self, value, connection):
        return self.to_python(value).__unicode__()
        
    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)