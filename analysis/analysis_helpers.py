import os
import json
import numpy as np
import re
import pandas as pd
import seaborn as sns
import matplotlib
from matplotlib import pylab, mlab, pyplot
from IPython.core.pylabtools import figsize, getfigs
plt = pyplot
import seaborn as sns
sns.set_context('poster')
sns.set_style('white')

exp_dir = './'

objcat = dict({'basset':'dog',
               'beetle':'car',
               'bloodhound':'dog',
               'bluejay':'bird',
               'bluesedan':'car',
               'bluesport':'car',
               'brown':'car',
               'bullmastiff':'dog',
               'chihuahua':'dog',
               'crow':'bird',
               'cuckoo':'bird',
               'doberman':'dog',
               'goldenretriever':'dog',
               'hatchback':'car',
               'inlay':'chair',
               'knob':'chair',
               'leather':'chair',
               'nightingale':'bird',
               'pigeon':'bird',
               'pug':'dog',
               'redantique':'car',
               'redsport':'car',
               'robin':'bird',
               'sling':'chair',
               'sparrow':'bird',
               'squat':'chair',
               'straight':'chair',
               'tomtit':'bird',
               'waiting':'chair',
               'weimaraner':'dog',
               'white':'car',
               'woven':'chair'
              })

def get_summary_stats(_D, all_games, correct_only=True):
    '''
    Get summary stats for sketchpad_basic experiment. 
    If correct_only is True, then filter to only include correct trials... except when calculating accuracy, which considers all trials.
    '''
    further_strokes = []
    closer_strokes = []
    further_svgLength = []
    closer_svgLength = []
    further_svgStd = []
    closer_svgStd = []
    further_svgLengthPS = []
    closer_svgLengthPS = []
    further_drawDuration = []
    closer_drawDuration = []
    further_accuracy = []
    closer_accuracy = []
    further_pixelintensity = []
    closer_pixelintensity = []
    for game in all_games:    
        if correct_only:
            D = _D[_D['outcome']==1]
        else:
            D = _D
        thresh = np.mean(D['numStrokes'].values) + 3*np.std(D['numStrokes'].values)
        tmp = D[(D['gameID']== game) & (D['condition'] == 'further') & (D['numStrokes'] < thresh)]['numStrokes']            
        further_strokes.append(tmp.mean())        
        tmp = D[(D['gameID']== game) & (D['condition'] == 'closer') & (D['numStrokes'] < thresh)]['numStrokes']
        closer_strokes.append(tmp.mean())
        further_svgLength.append(D[(D['gameID']== game) & (D['condition'] == 'further')]['svgStringLength'].mean())
        closer_svgLength.append(D[(D['gameID']== game) & (D['condition'] == 'closer')]['svgStringLength'].mean())
        further_svgStd.append(D[(D['gameID']== game) & (D['condition'] == 'further')]['svgStringStd'].mean())
        closer_svgStd.append(D[(D['gameID']== game) & (D['condition'] == 'closer')]['svgStringStd'].mean())    
        further_svgLengthPS.append(D[(D['gameID']== game) & (D['condition'] == 'further')]['svgStringLengthPerStroke'].mean())
        closer_svgLengthPS.append(D[(D['gameID']== game) & (D['condition'] == 'closer')]['svgStringLengthPerStroke'].mean())
        further_drawDuration.append(D[(D['gameID']== game) & (D['condition'] == 'further')]['drawDuration'].mean())
        closer_drawDuration.append(D[(D['gameID']== game) & (D['condition'] == 'closer')]['drawDuration'].mean())
        further_accuracy.append(_D[(_D['gameID']== game) & (_D['condition'] == 'further')]['outcome'].mean())
        closer_accuracy.append(_D[(_D['gameID']== game) & (_D['condition'] == 'closer')]['outcome'].mean())
        further_pixelintensity.append(D[(D['gameID']== game) & (D['condition'] == 'further')]['mean_intensity'].mean())
        closer_pixelintensity.append(D[(D['gameID']== game) & (D['condition'] == 'closer')]['mean_intensity'].mean())

    further_strokes, closer_strokes, further_svgLength, closer_svgLength, \
    further_svgStd, closer_svgStd, further_svgLengthPS, closer_svgLengthPS, \
    further_drawDuration, closer_drawDuration, further_accuracy, closer_accuracy, \
    further_pixelintensity, closer_pixelintensity = map(np.array, \
    [further_strokes, closer_strokes, further_svgLength, closer_svgLength,\
     further_svgStd, closer_svgStd, further_svgLengthPS, closer_svgLengthPS, \
    further_drawDuration, closer_drawDuration, further_accuracy, closer_accuracy, \
    further_pixelintensity, closer_pixelintensity])
    
    return further_strokes, closer_strokes, further_svgLength, closer_svgLength,\
     further_svgStd, closer_svgStd, further_svgLengthPS, closer_svgLengthPS, \
    further_drawDuration, closer_drawDuration, further_accuracy, closer_accuracy, \
    further_pixelintensity, closer_pixelintensity

    
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def sort_filelist(files):
    return files.sort(key=natural_keys)    
    
def get_close_accuracy_by_category(D, all_games):
    car_accuracy = []
    dog_accuracy = []    
    chair_accuracy = []
    bird_accuracy = []        
    for game in all_games:    
        car_accuracy.append(D[(D['category']=='car') & (D['condition']=='closer') & (D['gameID']== game) ]['outcome'].mean())
        dog_accuracy.append(D[(D['category']=='dog') & (D['condition']=='closer') & (D['gameID']== game) ]['outcome'].mean())     
        chair_accuracy.append(D[(D['category']=='chair') & (D['condition']=='closer') & (D['gameID']== game) ]['outcome'].mean())  
        bird_accuracy.append(D[(D['category']=='bird') & (D['condition']=='closer') & (D['gameID']== game) ]['outcome'].mean())   
    return bird_accuracy, car_accuracy, chair_accuracy, dog_accuracy
    
def get_canonical(category):    
    stimFile = os.path.join(exp_dir,'stimList_subord.js')
    with open(stimFile) as f:
        stimList = json.load(f)    
    allviews = [i['filename'] for i in stimList if i['basic']==category]
    canonical = [a for a in allviews if a[-8:]=='0035.png']    
    return canonical

def get_actual_pose(subordinate,pose):
    stimFile = os.path.join(exp_dir,'stimList_subord.js')
    with open(stimFile) as f:
        stimList = json.load(f)
    inpose = [i['filename'] for i in stimList if (i['subordinate']==subordinate) and (i['pose']==pose)]
    return inpose
    
def get_subord_names(category):
    full_names = get_canonical(category)    
    return [c.split('_')[2] for c in full_names]

def get_basic_names(subordinate):
    stimFile = os.path.join(exp_dir,'stimList_subord.js')
    with open(stimFile) as f:
        stimList = json.load(f)   
    allviews = [i['filename'] for i in stimList if i['subordinate']==subordinate]
    canonical = [a for a in allviews if a[-8:]=='0035.png']      
    return canonical[0].split('_')[0]

def build_url_from_category(category):
    full_names = get_canonical(category)
    url_prefix = 'https://s3.amazonaws.com/sketchloop-images-subord/'
    urls = []
    for f in full_names:
        urls.append(url_prefix + f)
    return urls

def build_url_from_filenames(filenames):
    url_prefix = 'https://s3.amazonaws.com/sketchloop-images-subord/'
    urls = []
    for f in filenames:
        urls.append(url_prefix + f)
    return urls

def plot_from_url(URL):
    file = cStringIO.StringIO(urllib.urlopen(URL).read())
    img = Image.open(file)    

def plot_gallery(category):
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec

    plt.figure(figsize = (8,8))
    gs1 = gridspec.GridSpec(8, 8)
    gs1.update(wspace=0.025, hspace=0.05)

    url_prefix = 'https://s3.amazonaws.com/sketchloop-images-subord/'
    for (i,c) in enumerate(category):
        URL = url_prefix + c
        file = cStringIO.StringIO(urllib.urlopen(URL).read())
        img = Image.open(file)
        p = plt.subplot(3,3,i+1)
        plt.imshow(img)
        p.get_xaxis().set_ticklabels([])
        p.get_yaxis().set_ticklabels([])
        p.get_xaxis().set_ticks([])
        p.get_yaxis().set_ticks([])
        p.set_aspect('equal')
        subord = c.split('_')[2]
        plt.title(subord)
    plt.tight_layout()

    
###### MODEL COMPARISON HELPERS ######

def load_json(path):
    with open(path) as f:
        J = json.load(f)   
    return J

def sumlogprob(a,b):
    if (a > b):
        return a + np.log1p(np.exp(b-a))
    else:
        return b + np.log1p(np.exp(a-b))  
    
dogs = sorted(['weimaraner', 'chihuahua', 'basset', 'doberman', 'bloodhound', 'bullmastiff', 'goldenretriever', 'pug'])
chairs = sorted(['leather', 'straight', 'squat', 'sling', 'woven', 'waiting', 'inlay','knob'])
birds = sorted(['crow', 'pigeon', 'robin', 'sparrow', 'tomtit', 'nightingale', 'bluejay', 'cuckoo'])
cars = sorted(['beetle', 'bluesport', 'brown', 'white', 'redsport', 'redantique', 'hatchback', 'bluesedan'])

def flatten_mcmc_to_samples(raw_params,num_samples=1000):
    flat_params = pd.DataFrame(columns=raw_params.columns)
    counter = 0
    for i,d in raw_params.iterrows():
        multiples = int(np.round(np.exp(d['posteriorProb'])*num_samples))
        for m in np.arange(multiples):
            flat_params.loc[counter] = d
            counter += 1

    ## correct the posteriorProb column so that each sample has prob 1/num_samples, where num_samples prob is 1000
    flat_params.drop(labels=['posteriorProb'], axis="columns", inplace=True)
    flat_params['posteriorProb'] = np.tile(np.log(1/num_samples),len(flat_params))
    assert len(flat_params)==num_samples
    return flat_params 

def flatten(x):
    return [item for sublist in x for item in sublist]

def bootstrapCI(x,nIter=1000):
    '''
    input: x is an array
    '''
    u = []
    for i in np.arange(nIter):
        inds = np.random.RandomState(i).choice(len(x),len(x))
        boot = x[inds]
        u.append(np.mean(boot))

    u = np.array(u)
    p1 = sum(u<0)/len(u) * 2
    p2 = sum(u>0)/len(u) * 2
    p = np.min([p1,p2])
    U = np.mean(u)
    lb = np.percentile(u,2.5)
    ub = np.percentile(u,97.5)
    return U,lb,ub,p

def make_category_by_obj_palette():
    import itertools
    col = []
    for j in sns.color_palette("hls", 4):
        col.append([i for i in itertools.repeat(j, 8)])
    return flatten(col)

def model_comparison_bars(model_prefixes,adaptor_type='human',split_type='balancedavg'):
    '''
    loads in model param posterior by adaptor type
    '''
    all_param_paths = sorted(os.listdir('../models/bdaOutput/{}_{}/raw/'.format(adaptor_type,split_type)))
    model_zoo = [i for i in all_param_paths for pre in model_prefixes if pre in i]
    model_zoo = [i for i in model_zoo if i[-1] != '~']
    model_zoo = [i for i in model_zoo if '.csv' in i]
    model_zoo = [i for i in model_zoo if 'S1' not in i.split('_')] ## do not consider S1
    
#     assert len(model_zoo) == len(model_prefixes)*4
    
    import analysis_helpers as h
    reload(h)

    LL = []
    model_name = []
    for this_model in model_zoo:

        ## define paths to model predictions
        if adaptor_type=='human':
            model_dirname = ('_').join(this_model.split('_')[:3])
        else:
            model_dirname = ('_').join(this_model.split('_')[:4])

        ## get file with params from this model
        this_params = os.path.join('../models/bdaOutput/{}_{}/raw/'.format(adaptor_type,split_type),this_model)
        params = pd.read_csv(this_params)
        assert np.round(np.sum(np.exp(params.posteriorProb.values)),12)==1

        ## append MAP LL
        LL.append(params.sort_values(by=['logLikelihood'],ascending=False).iloc[0]['logLikelihood'])
        model_name.append(model_dirname) 
        
    ## make dataframe
    PP = pd.DataFrame.from_records(zip(model_name,LL))
    PP.columns=['model','logLikelihood']
    if adaptor_type=='human':
        PP['perception'], PP['pragmatics'], PP['production'] = PP['model'].str.split('_', 3).str
    else:
        PP['adaptor'],PP['perception'], PP['pragmatics'], PP['production'] = PP['model'].str.split('_', 3).str
    return PP        
    
    
def plot_human_bars(PP):
    sns.catplot(data=PP,x='pragmatics',y='logLikelihood',
                   hue='production',kind='bar',
                   order=['S0','combined'],
                   hue_order=['nocost','cost'],
                   palette='Paired',
                   legend=False,
                   ci=None)
    plt.ylabel('log likelihood')
    locs, labels = plt.xticks([0,1],['insensitive','sensitive'],fontsize=14)
    plt.xlabel('context')
    # plt.ylim([-3000,0])
    plt.tight_layout()
    plt.savefig('./plots/loglikelihood_models_human.pdf')
    # plt.close()  
    
def plot_multimodal_bars(PP):
    sns.catplot(data=PP,x='perception',y='logLikelihood',
                   hue='pragmatics',kind='bar',
                   order=['pool1','conv42','fc6'],
                   palette='Paired',
                   legend=False,
                   ci=None)
    plt.ylabel('log likelihood')
    locs, labels = plt.xticks([0,1,2],['early','mid','high'],fontsize=14)
    plt.xlabel('visual features')
    # plt.ylim([-3000,0])
    plt.tight_layout()
    plt.savefig('./plots/loglikelihood_models_multimodal.pdf')
    # plt.close()      
    
def flatten_mcmc_to_samples(raw_params,num_samples=1000):
    flat_params = pd.DataFrame(columns=raw_params.columns)
    counter = 0
    for i,d in raw_params.iterrows():
        multiples = int(np.round(np.exp(d['posteriorProb'])*num_samples))
        for m in np.arange(multiples):
            flat_params.loc[counter] = d
            counter += 1

    ## correct the posteriorProb column so that each sample has prob 1/num_samples, where num_samples prob is 1000
    flat_params.drop(labels=['posteriorProb'], axis="columns", inplace=True)
    flat_params['posteriorProb'] = np.tile(np.log(1/num_samples),len(flat_params))
    assert len(flat_params)==num_samples
    return flat_params    

def check_mean_LL_for_cost_vs_nocost(model_prefixes=['multimodal_fc6'],
                                     adaptor_type = 'multimodal_fc6',
                                     split_type='balancedavg1',
                                     plot=True):
    
    all_param_paths = sorted(os.listdir('../models/bdaOutput/{}_{}/raw'.format(adaptor_type,split_type)))
    model_zoo = [i for i in all_param_paths for pre in model_prefixes if pre in i]
    model_zoo = [i for i in model_zoo if i[-1] != '~']
    model_zoo = [i for i in model_zoo if '.csv' in i]
    # model_zoo = [i for i in model_zoo if 'S1' not in i.split('_')] ## do not consider S1

    # assert len(model_zoo) == len(model_prefixes)*6

    ## get file with params from this model
    this_params = os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'raw',model_zoo[4])
    params1 = pd.read_csv(this_params)

    this_params = os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'raw',model_zoo[5])
    params2 = pd.read_csv(this_params)

    print 'Hold tight, running this check takes a little while...'
    ## "flatten" params file so that we have all 1000 samples in the params file itself
    fparams1 = flatten_mcmc_to_samples(params1)
    fparams2 = flatten_mcmc_to_samples(params2)
    fparams1.reset_index(inplace=True,drop=True)
    fparams2.reset_index(inplace=True,drop=True)

    print '{} cost version mean LL: {}'.format(adaptor_type, np.mean(fparams1.logLikelihood.values))
    print '{} nocost version mean LL: {}'.format(adaptor_type, np.mean(fparams2.logLikelihood.values))
    
    if plot==True:
        
        ## plot LL distribution comparing cost and nocost verisons
        plt.figure(figsize=(8,4))
        plt.subplot(121)
        h = sns.distplot(fparams1.logLikelihood.values,color=(0.6,0.2,0.2),label='cost')
        h = sns.distplot(fparams2.logLikelihood.values,color=(0.9,0.6,0.6),label='nocost')
        plt.xlabel('loglikelihood')
        # plt.xlim(-650,-400)
        plt.title(split_type)
        plt.legend()

        ## plot cost weight distribution
        plt.subplot(122)
        h = sns.distplot(fparams1.costWeight.values,color=(0.6,0.2,0.2))
        plt.title('cost param posterior')
        plt.xlabel('cost weight')
        
def flatten_param_posterior(adaptor_types = ['multimodal_pool1','multimodal_conv42','multimodal_fc6', 'human'],
                            verbosity=1):
    '''
    "flattening" means making sure that we have 1000 rows in each of the param posterior files, 
    corresponding to each sample. In "raw" form, there may be fewer than 1000 samples, b/c some samples
    might just be associated with higher posteriorProb.        
    '''
    model_prefixes = adaptor_types
    split_types = ['balancedavg{}'.format(i) for i in map(str,np.arange(1,6))]

    for adaptor_type in adaptor_types:
        if verbosity==1:
            print 'Flattening all splits and models of adaptor type {}...'.format(adaptor_type)        
        for split_type in split_types:
            if verbosity==1:
                print 'Now flattening models in split {}'.format(split_type)                         
            all_param_paths = sorted(os.listdir('../models/bdaOutput/{}_{}/raw'.format(adaptor_type,split_type)))
            model_zoo = [i for i in all_param_paths for pre in model_prefixes if pre in i]
            model_zoo = [i for i in model_zoo if i[-1] != '~']
            model_zoo = [i for i in model_zoo if '.csv' in i]    

            for i,model in enumerate(model_zoo):
                if verbosity>1:
                    print 'flattening {}'.format(model)
                ## get file with params from this model
                this_params = os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'raw',model)
                params = pd.read_csv(this_params)

                ## "flatten" params file so that we have all 1000 samples in the params file itself
                fparams = flatten_mcmc_to_samples(params)
                fparams.reset_index(inplace=True,drop=True)
                fparams = fparams.rename(columns={'id':'sample_id'}) ## rename id column to be sample id
                fparams = fparams.reindex(fparams.index.rename('id')) ## rename index column to be id column

                ## write out
                out_path = os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'flattened',model.split('.')[0] + 'Flattened.csv')
                if not os.path.exists(os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'flattened')):
                    os.makedirs(os.path.join('../models/bdaOutput/{}_{}'.format(adaptor_type,split_type),'flattened'))
                if verbosity>1:
                    print 'out_path = {}'.format(out_path)
                fparams.to_csv(out_path)
            
def get_sense_for_param_range_across_splits():
    
    '''
    Before running bda-enumerate in order to do model comparison, wanted to get a sense of the range that
    the various params fell into in the posterior, to ensure that our enumerate mesh captures this range for 
    all splits.
    '''

    split_types = ['balancedavg1','balancedavg2','balancedavg3','balancedavg4','balancedavg5']

    model_space = ['human_combined_cost','multimodal_fc6_combined_cost','multimodal_conv42_combined_cost',
                  'multimodal_fc6_S0_cost','multimodal_fc6_combined_nocost']

    # model_space = ['multimodal_fc6_combined_cost']

    # ## define paths to model predictions
    # split_type = 'balancedavg1'
    # model = 'multimodal_conv42_combined_cost'

    for model in model_space:
        print ' '
        for split_type in split_types:

            path_to_evaluate = '/data5/jefan/sketchpad_basic_model_output/evaluateOutput/{}_{}'.format(model,split_type)
            pred_files = [os.path.join(path_to_evaluate,i) for i in os.listdir(path_to_evaluate)]

            ## get file with params from this model
            if model.split('_')[0]=='human':
                bdaOutDir = '_'.join(model.split('_')[:1]) + '_{}'.format(split_type)
            else:
                bdaOutDir = '_'.join(model.split('_')[:2]) + '_{}'.format(split_type)
            params_fname = model + '_' + split_type + 'ParamsFlattened.csv'
            params_path = os.path.join('../models/bdaOutput',bdaOutDir,'flattened',params_fname)
            params = pd.read_csv(params_path)

            maxSim = np.max(params.simScaling.values)
            maxPrag = np.max(params.pragWeight.values)
            maxCost = np.max(params.costWeight.values)
            maxInf = np.max(params.infWeight.values)

            print 'model {} split {}'.format(model,split_type)
            print 'max | sim: {} prag: {} cost: {} inf: {}'.format(maxSim,maxPrag,maxCost,maxInf) 
            
def weight_cost_by_modelProb(x):
    '''
    in order to determine the average sketch cost predicted by the model for this trial,
    take mean cost across all sketch categories weighted by the probability assigned to that sketch category
    
    note: modelProb is in log space, so you need to exponentiate before multiplying by cost
    '''
    return np.exp(x['modelProb']) * x['cost']            