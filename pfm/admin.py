
from django.contrib import admin
from pfm.models import PfmTest, PfmList

class PfmTestAdmin(admin.ModelAdmin):
    list_display = (
        'test_idx', 'gender', 'accord', 'note', 'sillage', 'age', 'testingDate'
    )
admin.site.register(PfmTest, PfmTestAdmin)
class PfmListAdmin(admin.ModelAdmin):
    list_display = (
        'list_idx', 
        'brand_kor', 
        'name_kor', 
        'accords', 
        'notes', 
        'longevity_rate', 
        'sillage_rate',
        'male',
        'female',
        'rating_score',
        'brand_eng',
        'name_eng',
        'votes',
    )
    
admin.site.register(PfmList, PfmListAdmin)



