import cmd #cmd는 별도의 설치 필요없음!
import pickle
import os
import pandas as pd

ml_title = pd.read_csv("/opt/ml/input/fighting/CSV/ml_title.csv")
mbti_all_title = pd.read_csv("/opt/ml/input/fighting/CSV/mbti_all_title.csv")
mbti_none_title = pd.read_csv("/opt/ml/input/fighting/CSV/mbti_none_title.csv")

ml_title = ml_title.dropna(axis=0)

title_list = list(ml_title['title'])
mbti_none_title_list = list(mbti_none_title['Contents'])

start_index = 0 #300
i = start_index

if os.path.exists('real_none_title.pickle'):
    with open('real_none_title.pickle', 'rb') as f:
        real_none_title = pickle.load(f)
else:
    real_none_title = []
    
if os.path.exists('dont_know_title.pickle'):
    with open('dont_know_title.pickle', 'rb') as f:
        dont_know_title = pickle.load(f)
else:
    dont_know_title = []
    
if os.path.exists('series_title.pickle'):
    with open('series_title.pickle', 'rb') as f:
        series_title = pickle.load(f)
else:
    series_title = []


def content_based_filtering_jaccard(title_list, title):
    topn=3
    target_split_set = set(title.split())
    sim_list = []
    sim_df = pd.DataFrame(title_list, columns=['title'])
    for idx, movie in enumerate(title_list):
        title_split_set = set(movie.split())
        title_intersection = target_split_set.intersection(title_split_set)
        jac_sim = float(len(title_intersection)) / (len(target_split_set) + len(title_split_set) - len(title_intersection))
        sim_list.append(jac_sim)
    sim_df['jaccard_similarity'] = sim_list

    return sim_df.sort_values('jaccard_similarity', ascending=False).reset_index(drop=True)[:topn]


def show_mbti_title_and_top3(i):
    global tmp
    print(f'{i}번째 mbti title : \033[1;34m{mbti_none_title_list[i]}\033[0m')

    #가장 유사한 Top3 영화 출력부분
    tmp = content_based_filtering_jaccard(title_list, mbti_none_title_list[i])
    tmp.index = range(1, 4)
    print(f'[1]\t\t  \033[1;32m{tmp.loc[1].title}\033[0m\t\t\t{tmp.loc[1].jaccard_similarity}')
    print(f'[2]\t\t  \033[1;32m{tmp.loc[2].title}\033[0m\t\t\t{tmp.loc[2].jaccard_similarity}')
    print(f'[3]\t\t  \033[1;32m{tmp.loc[3].title}\033[0m\t\t\t{tmp.loc[3].jaccard_similarity}')

    
class MyPrompt(cmd.Cmd):
    intro = '입력받은 title(from MBTI)과 가장 유사한 \033[1mtitle(from ML) 3개(1/2/3) 중\033[0m 고르면 알아서 데이터프레임에 담아줍니다!\n\
\033[1m비슷한 영화제목이 없는 경우엔 0를\033[0m 눌러주세요!\n\
\033[1m시작하는 방법은 start\033[0m입니다.\n\
\033[1m종료하는 방법은 quit\033[0m이며, 자동으로 데이터프레임을 저장해줍니다!'
    prompt = '(my_shell) '
    result_df = pd.DataFrame()
        
    def do_start(self, arg):
        global i, title_list, mbti_none_title_list
        show_mbti_title_and_top3(i)
    
    def do_1(self, arg):
        global i, title_list, mbti_none_title_list, tmp, result_df
        try:
            result_df.loc[i] = {"mbti_title":mbti_none_title_list[i], \
                                "ml_title":tmp.iloc[0].title}
        except:
            result_df = pd.DataFrame({"mbti_title":[mbti_none_title_list[i]], \
                                      "ml_title":[tmp.iloc[0].title]})
            
        i += 1
        show_mbti_title_and_top3(i)
        
    def do_2(self, arg):
        global i, title_list, mbti_none_title_list, tmp, result_df
        try:
            result_df.loc[i] = {"mbti_title":mbti_none_title_list[i], \
                                "ml_title":tmp.iloc[1].title}
        except:
            result_df = pd.DataFrame({"mbti_title":[mbti_none_title_list[i]], \
                                      "ml_title":[tmp.iloc[1].title]})
        i += 1
        show_mbti_title_and_top3(i)
        
    def do_3(self, arg):
        global i, title_list, mbti_none_title_list, tmp, result_df
        try:
            result_df.loc[i] = {"mbti_title":mbti_none_title_list[i], \
                                "ml_title":tmp.iloc[2].title}
        except:
            result_df = pd.DataFrame({"mbti_title":[mbti_none_title_list[i]], \
                                      "ml_title":[tmp.iloc[2].title]})
        i += 1
        show_mbti_title_and_top3(i)
        
    def do_x(self, arg):
        global i
        real_none_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top3(i)
        
    def do_d(self, arg):
        global i
        dont_know_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top3(i)
    
    def do_s(self, arg):
        global i
        series_title.append((i,mbti_none_title_list[i]))
        i += 1
        show_mbti_title_and_top3(i)
        
    def do_quit(self, arg):
        global result_df
        try:
            result_df.to_csv(f'result_{start_index}부터_{i}까지.csv')
        except: pass
        with open('real_none_title.pickle', 'wb') as f:
            pickle.dump(real_none_title, f)
        with open('dont_know_title.pickle', 'wb') as f:
            pickle.dump(dont_know_title, f)
        with open('series_title.pickle', 'wb') as f:
            pickle.dump(series_title, f)
        print(f"저장된 파일이름: result_{start_index}부터_{i}까지.csv\n")
        print("비슷한 영화제목이 없는 경우 리스트: real_none_title")
        return True
    
if __name__ == '__main__':
    MyPrompt().cmdloop()