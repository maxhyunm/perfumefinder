from django.http import HttpResponse, HttpRequest
from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.http import urlquote
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from pfm.models import PfmTest, PfmList, Accords, Aroma, Notes
import django
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import quote
from sympy.integrals.rubi.utility_function import Rt

@csrf_exempt
def main(request):
    return render(request, 'main.html')

@csrf_exempt
def result1(request):
    try :
        # 데이터셋 불러오기
        df = pd.DataFrame(list(PfmList.objects.all().values()))
        df = df.reset_index()

        # 성별 정리(성별에 따른 데이터 정리)
        error = "성별"
        gend=request.POST['gender']
        if gend == 'male' :
            df = df[df['male']==1]
            df = df.reset_index()
        elif gend == 'female' :
            df = df[df['female']==1]
            df = df.reset_index()

        # 어코드용 cv 준비
        cv = CountVectorizer()
        cv_accords = cv.fit_transform(df['accords'])

        # 어코드 정리
        keyacc = request.POST.getlist('accord[]')
        if len(keyacc) == 0 :
            error = '조합'
            raise Exception

        # 어코드 일치 데이터 찾기(cv)
        acc_pf = np.asarray(cv_accords.toarray())[:, [cv.vocabulary_.get(i) for i in keyacc]]
        acc_score = acc_pf.sum(axis=1)
        acc_score = acc_score.argsort()[::-1]

        # 노트용 cv 준비
        cv2 = CountVectorizer()
        cv_notes = cv2.fit_transform(df['notes'])


        # 노트 정리
        keynote = request.POST.getlist('note[]')
        if len(keynote) == 0 :
            error = '노트'
            raise Exception

        # 노트 일치 데이터 찾기(cv)
        note_pf = np.asarray(cv_notes.toarray())[:, [cv2.vocabulary_.get(i) for i in keynote]]
        note_score = note_pf.sum(axis=1)
        note_score = note_score.argsort()[::-1]


        # 노트와 어코드 일치하는 중복데이터 찾기
        finaldf = pd.DataFrame(columns=df.columns)
        for i in acc_score :
            for j in note_score :
                if i==j :
                    if len(finaldf.index) < 5 :
                        finaldf = finaldf.append(df.loc[i])
                    else :
                        break

        # 확산력에 따른 정렬
        error = "확산력"
        slg  =request.POST['sillage']

        if slg == 'low' :
            finaldf = finaldf.sort_values(by=['sillage_rate'], ascending=True)
        else :
            finaldf = finaldf.sort_values(by=['sillage_rate'], ascending=False)

        # 상위 5개 뽑아서 브랜드명, 향수명, 어코드, 노트 저장
        nums = list(range(1,6))
        brands = list(finaldf['brand_kor'])
        pfms = list(finaldf['name_kor'])
        acds = list(finaldf['accords'])
        nts = list(finaldf['notes'])

        # 이미지명 뽑기 위하여 영문 브랜드명, 향수명 저장
        eb = list(finaldf['brand_eng'])
        en = list(finaldf['name_eng'])

        # 이미지명 목록으로 저장
        pf_img = []
        for b, n in zip(eb, en) :
            pf_img.append('img/'+b+'_'+n+'.jpg')

        # 한글 이름을 검색창 주소로 넣기 위한 인코딩작업
        br_quote = []
        pf_quote = []
        for i in brands :
            br_quote.append(quote(i))
        for i in pfms :
            pf_quote.append(quote(i))

        # 최종파일 zip
        zips1 = zip(br_quote, pf_quote, pf_img)
        zips2 = zip(nums, brands, pfms, br_quote,  pf_quote)
        zips3 = zip(acds, nts)

        # 데이터저장용 작업
        accstr = ''
        notstr = ''

        for a in keyacc :
            accstr += a
            accstr += ','
        for n in keynote :
            notstr += n
            notstr += ','

        error = '나이'
        ag = request.POST['age']


        dto = PfmTest(
                    gender = gend,
                    accord = accstr,
                    note = notstr,
                    sillage = slg,
                    age = ag
                    )
        dto.save()

        # 리턴
        return render(request, 'result.html',
                      {'zips1' : zips1,
                       'zips2' : zips2,
                       'zips3' : zips3})

    # 오류시 오류페이지 리턴
    except :
        return render(request, 'error.html',
                      {'error' : error
                      })

@csrf_exempt
def result2(request):
    try :
        # 데이터셋 불러오기
        df = pd.DataFrame(list(PfmList.objects.all().values()))
        df = df.reset_index()
        # 노트용 cv 및 cs 준비
        cv3 = CountVectorizer()
        cvX = cv3.fit_transform(df['notes'])
        cosim = cosine_similarity(cvX)

        # 브랜드명/제품명 일치하는 정보 불러와서 인덱스넘버 뽑기
        brand = request.POST['brand']
        if len(brand) == 0 :
            error = "브랜드"
            raise Exception
        pfm = request.POST['pfm']
        if len(pfm) == 0 :
            error = "제품명"
            raise Exception
        sel_df = df[(df['brand_kor']==brand)&(df['name_kor']==pfm)]
        idxnum = sel_df.index.item()

        # cs를 돌려 데이터프레임으로 저장, 전달받은 향수와 똑같은 제품은 제거하고 유사도순 정렬
        simillist = pd.DataFrame({'cos':cosim[idxnum], 'idx':np.arange(len(cosim[idxnum]))})
        simillist = simillist.drop(idxnum, axis=0)
        sim_sort = simillist.sort_values('cos', ascending=False)

        # 5개를 추려 리스트에 추가 > 해당 인덱스넘버의 제품 데이터셋을 가져와서 데이터프레임 만들기
        nums = []
        for i in range(5) :
            nums.append(int(sim_sort.iloc[i][1]))
        finaldf = pd.DataFrame(columns=df.columns)
        for n in nums :
            finaldf = finaldf.append(df.loc[n])

        # 리턴용 리스트 제작(브랜드명, 제품명, 어코드, 노트)
        nums = list(range(1,6))
        brands = list(finaldf['brand_kor'])
        pfms = list(finaldf['name_kor'])
        acds = list(finaldf['accords'])
        nts = list(finaldf['notes'])

        # 이미지명 뽑기 위하여 영문 브랜드명, 향수명 저장
        eb = list(finaldf['brand_eng'])
        en = list(finaldf['name_eng'])

        # 이미지 이름 불러오기
        pf_img = []
        for b, n in zip(eb, en) :
            pf_img.append('img/'+b+'_'+n+'.jpg')

        # 한글 이름을 검색창 주소로 넣기 위한 인코딩작업
        br_quote = []
        pf_quote = []
        for i in brands :
            br_quote.append(quote(i))
        for i in pfms :
            pf_quote.append(quote(i))


        # 최종파일 zip
        zips1 = zip(br_quote,  pf_quote, pf_img)
        zips2 = zip(nums, brands, pfms, br_quote,  pf_quote)
        zips3 = zip(acds, nts)


        # 데이터저장용
        error = '평점'
        rt = request.POST['rate']
        if rt == 'pass' :
            pass
        else :
            rt = int(rt)
            listid = idxnum+1
            error = '불러오기'
            selectpfm = PfmList.objects.get(list_idx=listid)
            error = 'rate추가'
            selectpfm.before_avg_rate += rt
            error = 'vote추가'
            selectpfm.votes += 1
            selectpfm.save()
            selectpfm = PfmList.objects.get(list_idx=listid)
            error = '평균내기'
            selectpfm.rating_score = selectpfm.before_avg_rate/selectpfm.votes
            error = '저장'
            selectpfm.save()

        # 리턴
        return render(request, 'result.html',
                      {'zips1' : zips1,
                       'zips2' : zips2,
                       'zips3' : zips3})

    # 오류시 에러페이지 리턴
    except :
        return render(request, 'error.html',
                      {'error' : error
                      })

@csrf_exempt
def test1(request):
    aclist = pd.DataFrame(list(Accords.objects.all().values()))
    aclist = aclist.reset_index()
    ntlist = pd.DataFrame(list(Notes.objects.all().values()))
    ntlist = ntlist.reset_index()

    accs = list(aclist['accord'])
    cons = list(aclist['content'])
    acczip = zip(accs, cons)

    nots = list(ntlist['note'])
    cons2 = list(ntlist['content'])
    renots = list(ntlist['noterename'])
    notzip = zip(nots, cons2)
    notenames = zip(nots, renots)

    return render(request, 'test1.html',
                  {'acczip' : acczip,
                   'notzip' : notzip,
                   'accs' : accs,
                   'notenames' : notenames})

@csrf_exempt
def test2(request):
    df = pd.DataFrame(list(PfmList.objects.all().values()))
    df = df.reset_index()
    brands = list(df['brand_kor'].unique())

    return render(request, 'test2.html',
                  {'brands' : brands})

@csrf_exempt
def getpfmlist(request):
    df = pd.DataFrame(list(PfmList.objects.all().values()))
    df = df.reset_index()
    brand = request.POST['brand']
    df = df[df['brand_kor']==brand].sort_values('name_kor')
    pfms = list(df['name_kor'].unique())

    return render(request, 'test2.html',
                  {'selbrand' : brand,
                   'pfms' : pfms})

@csrf_exempt
def err(request):
    return render(request, 'error.html')

@csrf_exempt
def top10(request):
    # 데이터셋 불러오기
    #df = pd.read_csv('df.csv', encoding='cp949')
    df = pd.DataFrame(list(PfmList.objects.all().values()))
    df = df.reset_index()

    nums = list(range(1,11))

    # 총순위용 데이터
    total_top10 = df[df['votes']>=1000].sort_values('rating_score', ascending=False).head(10)
    total_brands = list(total_top10['brand_kor'])
    total_pfms = list(total_top10['name_kor'])

    # 총순위 이미지 정리용
    total_eb = list(total_top10['brand_eng'])
    total_en = list(total_top10['name_eng'])
    total_img = []
    for b, n in zip(total_eb, total_en) :
        total_img.append('img/'+b+'_'+n+'.jpg')

    # 총순위 주소 경로 인코딩용
    total_br_quote = []
    total_pf_quote = []
    for i in total_brands :
        total_br_quote.append(quote(i))
    for i in total_pfms :
        total_pf_quote.append(quote(i))

    # 총순위 정보 zip
    total_zip = zip(nums, total_brands, total_pfms,total_br_quote,  total_pf_quote, total_img)

    # 남성순위용 데이터
    male_top10 = df[(df['votes']>=1000)&(df['male']==1)].sort_values('rating_score', ascending=False).head(10)
    male_brands = list(male_top10['brand_kor'])
    male_pfms = list(male_top10['name_kor'])

    # 남성순위 이미지 정리용
    male_eb = list(male_top10['brand_eng'])
    male_en = list(male_top10['name_eng'])
    male_img = []
    for b, n in zip(male_eb, male_en) :
        male_img.append('img/'+b+'_'+n+'.jpg')

    # 남성순위 주소 경로 인코딩용
    male_br_quote = []
    male_pf_quote = []
    for i in male_brands :
        male_br_quote.append(quote(i))
    for i in male_pfms :
        male_pf_quote.append(quote(i))

    # 남성순위 정보 zip
    male_zip = zip(nums, male_brands, male_pfms, male_br_quote,  male_pf_quote, male_img)

    # 여성순위용 데이터
    female_top10 = df[(df['votes']>=1000)&(df['female']==1)].sort_values('rating_score', ascending=False).head(10)
    female_brands = list(female_top10['brand_kor'])
    female_pfms = list(female_top10['name_kor'])

    # 여성순위 이미지 정리용
    female_eb = list(female_top10['brand_eng'])
    female_en = list(female_top10['name_eng'])
    female_img = []
    for b, n in zip(female_eb, female_en) :
        female_img.append('img/'+b+'_'+n+'.jpg')

    # 여성순위 주소 경로 인코딩용
    female_br_quote = []
    female_pf_quote = []
    for i in female_brands :
        female_br_quote.append(quote(i))
    for i in female_pfms :
        female_pf_quote.append(quote(i))

    # 여성순위 정보 zip
    female_zip = zip(nums, female_brands, female_pfms, female_br_quote, female_pf_quote, female_img)

    # 지속력순위용 데이터
    longevity_top10 = df[df['votes']>=1000].sort_values('longevity_rate', ascending=False).head(10)
    longevity_brands = list(longevity_top10['brand_kor'])
    longevity_pfms = list(longevity_top10['name_kor'])

    # 지속력순위 이미지 정리용
    longevity_eb = list(longevity_top10['brand_eng'])
    longevity_en = list(longevity_top10['name_eng'])
    longevity_img = []
    for b, n in zip(longevity_eb, longevity_en) :
        longevity_img.append('img/'+b+'_'+n+'.jpg')

    # 지속력순위 주소 경로 인코딩용
    longevity_br_quote = []
    longevity_pf_quote = []
    for i in longevity_brands :
        longevity_br_quote.append(quote(i))
    for i in longevity_pfms :
        longevity_pf_quote.append(quote(i))

    # 지속력순위 정보 zip
    longevity_zip = zip(nums, longevity_brands, longevity_pfms, longevity_br_quote,  longevity_pf_quote, longevity_img)

    # 확산력순위용 데이터
    sillage_top10 = df[df['votes']>=1000].sort_values('sillage_rate', ascending=False).head(10)
    sillage_brands = list(sillage_top10['brand_kor'])
    sillage_pfms = list(sillage_top10['name_kor'])

    # 확산력순위 이미지 정리용
    sillage_eb = list(sillage_top10['brand_eng'])
    sillage_en = list(sillage_top10['name_eng'])
    sillage_img = []
    for b, n in zip(sillage_eb, sillage_en) :
        sillage_img.append('img/'+b+'_'+n+'.jpg')

    # 확산력순위 주소 경로 인코딩용
    sillage_br_quote = []
    sillage_pf_quote = []
    for i in sillage_brands :
        sillage_br_quote.append(quote(i))
    for i in sillage_pfms :
        sillage_pf_quote.append(quote(i))

    # 확산력순위 정보 zip
    sillage_zip= zip(nums, sillage_brands, sillage_pfms, sillage_br_quote,  sillage_pf_quote, sillage_img)

    # 타이틀 이름
    titles = ['total', 'male', 'female', 'longevity', 'sillage']

    # 리턴 내용
    return render(request, 'list.html',
                  {'total_zip' : total_zip,
                  'male_zip' : male_zip,
                  'female_zip' : female_zip,
                  'longevity_zip' : longevity_zip,
                  'sillage_zip' : sillage_zip,
                  'titles' : titles
                  })

@csrf_exempt
def aroma(request):
    ardf = pd.DataFrame(list(Aroma.objects.all().values()))
    ardf = ardf.reset_index()

    nk = list(ardf['note_ko'])
    ne = list(ardf['note_en'])
    nr = list(ardf['noterename'])
    nc = list(ardf['content'])

    arzip = zip(nk, ne, nr, nc)
    namezip = zip(nr, ne, nk)

    return render(request, 'aroma.html',
                  {'arzip' : arzip,
                   'namezip' : namezip})


@csrf_exempt
def result3(request):
    try :
        # 데이터셋 불러오기
        df = pd.DataFrame(list(PfmList.objects.all().values()))
        df = df.reset_index()

        # 노트용 cv 준비
        cv4 = CountVectorizer()
        cv_aroma = cv4.fit_transform(df['notes'])

        # 노트정보 불러오기
        error = '노트'
        keynote = request.POST.getlist('note[]')
        if len(keynote) == 0 :
            raise Exception

        # 노트내용 일치하는 데이터 찾기(cv)
        note_pf = np.asarray(cv_aroma.toarray())[:, [cv4.vocabulary_.get(i) for i in keynote]]
        note_score = note_pf.sum(axis=1)
        note_score = note_score.argsort()[::-1]

        # 찾은 데이터를 데이터프레임으로 저장하고, 순위별로 3개까지 추리기
        finaldf = pd.DataFrame(columns=df.columns)
        for i in note_score :
            if len(finaldf.index) < 3 :
                finaldf = finaldf.append(df.loc[i])
            else :
                break

        # 출력용 데이터 정보
        nums = list(range(1,4))
        brands = list(finaldf['brand_kor'])
        pfms = list(finaldf['name_kor'])
        acds = list(finaldf['accords'])
        nts = list(finaldf['notes'])

        # 이미지 파일명 저장
        eb = list(finaldf['brand_eng'])
        en = list(finaldf['name_eng'])
        pf_img = []
        for b, n in zip(eb, en) :
            pf_img.append('img/'+b+'_'+n+'.jpg')

        # 인코딩용 제품명 저장
        br_quote = []
        pf_quote = []
        for i in brands :
            br_quote.append(quote(i))
        for i in pfms :
            pf_quote.append(quote(i))

        # 최종파일 zip
        zips1 = zip(br_quote,  pf_quote, pf_img)
        zips2 = zip(nums, brands, pfms, br_quote,  pf_quote)
        zips3 = zip(acds, nts)

        # 리턴
        return render(request, 'result.html',
                      {'zips1' : zips1,
                       'zips2' : zips2,
                       'zips3' : zips3,})

    # 예외발생시 에러처리
    except :
        return render(request, 'error.html',
                      {'error' : error})