from django.db import models
from datetime import datetime

# Create your models here.
class PfmTest(models.Model):
    
    #autofield index
    test_idx = models.AutoField(primary_key=True)
    
    #성별
    gender = models.TextField(null=False)
    
    #선호하는 accord
    accord = models.TextField(null=False)
    
    #선호하는 note
    note = models.TextField(null=False)
    
    #선호하는 확산력
    sillage = models.TextField(null=False)
    
    #나이대
    age = models.TextField(null=False)
    
    #등록시간
    testingDate = models.DateTimeField(default=datetime.now(), blank=True)
    
class PfmList(models.Model):
    
    #autofield index
    list_idx = models.AutoField(primary_key=True)
    
    # 한국브랜드명
    brand_kor = models.TextField(null=False)
    
    # 한국제품명
    name_kor = models.TextField(null=False)
    
    # 어코드
    accords = models.TextField(null=False)
    
    # 노트
    notes = models.TextField(null=False)
    
    # 지속력    
    longevity_rate = models.DecimalField(max_digits = 4, decimal_places = 3, null=False)
    
    # 확산력
    sillage_rate = models.DecimalField(max_digits = 4, decimal_places = 3, null=False)
    
    # 남성용
    male = models.BigIntegerField(null=False)
    
    # 여성용
    female = models.BigIntegerField(null=False)
    
    # 평점
    rating_score = models.DecimalField(max_digits = 4, decimal_places = 3, null=False)
    
    # 영문브랜드명
    brand_eng = models.TextField(null=False)
    
    # 영문제품명
    name_eng = models.TextField(null=False)
    
    # 투표수
    votes = models.BigIntegerField(null=False)
    
    # 총점
    before_avg_rate = models.BigIntegerField(null=True)





class Df(models.Model):
    df_idx = models.AutoField(primary_key=True)
    brand_kor = models.TextField(blank=True, null=True)
    name_kor = models.TextField(blank=True, null=True)
    accords = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    longevity_rate = models.FloatField(blank=True, null=True)
    sillage_rate = models.FloatField(blank=True, null=True)
    male = models.IntegerField(blank=True, null=True)
    female = models.IntegerField(blank=True, null=True)
    rating_score = models.FloatField(blank=True, null=True)
    brand_eng = models.TextField(blank=True, null=True)
    name_eng = models.TextField(blank=True, null=True)
    votes = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'df'


class Accords(models.Model):
    acc_idx = models.AutoField(primary_key=True)
    accord = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accords'



class Aroma(models.Model):
    arom_idx = models.AutoField(primary_key=True)
    note_ko = models.TextField(blank=True, null=True)
    note_en = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    noterename = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aroma'




class Notes(models.Model):
    note_idx = models.AutoField(primary_key=True)
    note = models.TextField(blank=True, null=True)
    noterename = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notes'



