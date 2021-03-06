import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import shap
shap.initjs()
import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import streamlit.components.v1 as components
import joblib,os,pickle,warnings
warnings.filterwarnings('ignore')
import seaborn as sns
color=sns.cubehelix_palette(start=.5, rot=-.5, as_cmap=True)
import lightgbm as lgb
st.set_page_config(layout="wide")
st.title("Tableaux de bord pour prédire un défaut de remboursement de crédit")
st.subheader("Ce tableau de bord permet de prédire si un client est capable ou non capable de rembourser un crédit")

#X_test_final=pd.read_pickle("https://github.com/SidiML/Projet_Scoring/blob/master/X_test_final?raw=true")
#@st.cache()
X_test_final=pd.read_csv("https://raw.githubusercontent.com/SidiML/Projet7/master/X_test_final.csv")
#X_train_final=pd.read_csv("C:/Users/admin/OneDrive/Bureau/Openclassroom/Projet7/X_train_final.csv")
#X_val_final=pd.read_csv("C:/Users/admin/OneDrive/Bureau/Openclassroom/Projet7/X_val_final.csv")

#X_train_final.set_index("SK_ID_CURR", inplace = True)
#X_val_final.set_index("SK_ID_CURR", inplace = True)
#X_test_final.set_index("SK_ID_CURR", inplace = True)


#y_train = pd.read_pickle("C:/Users/admin/OneDrive/Bureau/Openclassroom/Projet7/y_train")
#y_val = pd.read_pickle("C:/Users/admin/OneDrive/Bureau/Openclassroom/Projet7/y_val")
y_test = pd.read_pickle("https://raw.githubusercontent.com/SidiML/Projet7/master/y_test")

#####################################
fileName="https://github.com/SidiML/Projet7/blob/master/my_model.joblib?raw=true"
with open(fileName, 'r') as f:
    clf1 = joblib.load(f)

fileName="https://github.com/SidiML/Projet7/blob/master/my_feature.joblib?raw=true"
with open(fileName, 'r') as f:
    selected_features = joblib.load(f)
##################################################
predict_test=clf1.predict(X_test_final[selected_features])
#print(classification_report(y_test,predict_test))
predict_prob_test=clf1.predict_proba(X_test_final[selected_features])
#pd.DataFrame(confusion_matrix(y_test,predict_test,normalize='true'))
df=X_test_final[selected_features].copy()
df['predict']=predict_test
df['proba']=predict_prob_test[:,1]
#plot_confusion_matrix(y_test, predict_test)


#lgb.plot_importance(clf1, ax=None, height=0.2, xlim=None, ylim=None, title='Feature importance', xlabel='Feature importance',
#					ylabel='Features', importance_type='split', max_num_features=25, ignore_zero=True, figsize=(22, 20), dpi=None, grid=True, precision=3)
#plt.show()

#################
if st.checkbox('Montrez la table'):
	st.subheader('Voici les données')
	st.dataframe(df)

def st_shap(plot, height=200,width=870):
	shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
	components.html(shap_html, height=height,width=width)


#@st.cache()
def get_data():
    links="https://raw.githubusercontent.com/SidiML/Projet7/master/data_train1.csv"
    return pd.read_csv(links)

df1 = get_data()

df1.set_index('SK_ID_CURR',inplace=True)
df1['AGE']=round(np.abs(df1['DAYS_BIRTH']/365)).astype(int)

st.sidebar.title('PROFIL CLIENT')
#id_client = st.sidebar.number_input("Entrez l'ID du client.")
id_client=st.sidebar.selectbox("Selectionnez l'identifiant du client", options=(df.index))
if id_client in list(df.index):
	a=(int(id_client))

	#st.sidebar.subheader("Profil CLIENT")
	st.sidebar.markdown(f'**Sexe:**<div style="color: green; font-size: medium">{df1["CODE_GENDER"].loc[a]}</div>',unsafe_allow_html=True)
	st.sidebar.markdown(f'**Profession:**<div style="color: green; font-size: medium">{df1["OCCUPATION_TYPE"].loc[a]}</div>',unsafe_allow_html=True)
	st.sidebar.markdown(f'**Source du Revenu:**<div style="color: green; font-size: medium">{df1["NAME_INCOME_TYPE"].loc[a]}</div>',unsafe_allow_html=True)
	st.sidebar.markdown(f'**Situation Familiale:**<div style="color: green; font-size: medium">{df1["NAME_FAMILY_STATUS"].loc[a]}</div>',unsafe_allow_html=True)
	st.sidebar.markdown(f'**Niveau d\'Etude:**<div style="color: green; font-size: medium">{df1["NAME_EDUCATION_TYPE"].loc[a]}</div>',unsafe_allow_html=True)
	st.sidebar.markdown(f'**Age:**<div style="color: green; font-size: medium">{df1["AGE"].loc[a]}</div>',unsafe_allow_html=True)


	b=np.round(df['proba'].loc[a],3)

	col1, col2= st.beta_columns(2)

	with col1:
		st.markdown("**IDENTIFIANT**")
		st.write("L'identifiant du client est:",a, use_column_width=True)
	with col2:
		st.markdown("**PROBABILITE**")
		st.write("Probabilité de ne pas rembourser est:",b,use_column_width=True)


	#lgbm_explainer = shap.TreeExplainer(model = clf1, model_output='margin')
    fileName="https://github.com/SidiML/Projet7/blob/master/my_shap_model.joblib?raw=true"
    with open(fileName, 'r') as f:
        lgbm_explainer = joblib.load(f)

    shap_values =lgbm_explainer.shap_values(df.drop(['predict','proba'],1).loc[[a]])

	vals= np.abs(shap_values).mean(0)
	feature_importance = pd.DataFrame(list(zip(df.drop(['predict','proba'],1).loc[[a]], vals)), columns=['col_name','feature_importance'])
	feature_importance.sort_values(by=['feature_importance'], ascending=False,inplace=True)


	st.sidebar.title("Features Importantes")
	if st.sidebar.checkbox("Voir les features"):
		st.sidebar.subheader('Les variables importantes')
		st.sidebar.dataframe(feature_importance)

	st.sidebar.subheader('Graphe de Décision')
	fig2, ax = plt.subplots(nrows=1, ncols=1)
	shap.summary_plot(shap_values, df.drop(['predict','proba'],1).loc[[a]], plot_type="bar")
	st.sidebar.pyplot(fig2,use_column_width=True)



	# plot the SHAP values for the 10th observation
	st_shap(shap.force_plot(lgbm_explainer.expected_value, shap_values, df.drop(['predict','proba'],1).loc[[a]]))



	col1, col2= st.beta_columns(2)
	with col1:
		st.subheader("Comparaison du Client avec la moyenne des Clients")
		cols=['EXT_SOURCE_1','EXT_SOURCE_2','EXT_SOURCE_3','AGE','CREDIT_TERM','AMT_ANNUITY','DAYS_BIRTH','DAYS_EMPLOYED']
		colonnes=st.selectbox("Selectionnez une Variable", options=(cols))
		average_hold=df1.groupby(['TARGET']).mean()
		b1=round(df1.loc[a][colonnes],2)
		b2=round(average_hold[colonnes].values[0],2)
		b3=round(average_hold[colonnes].values[1],2)
		# intialise data of lists.
		x1 = ['CLIENT', 'AVERAGE_CLIENT_REPAID', 'AVERAGE_CLIENT_NO_REPAID']
		y1 = [b1,b2 ,b3]
		# Use textposition='auto' for direct text
		colors = ['#17becf',] * 3
		colors[0] = 'crimson'
		#fig = go.Figure(data=[go.Bar(x=x1, y=y1,text=y1,textposition='auto',marker_color=colors)])
		data = [go.Bar(x=x1, y=y1,text=y1,textposition='auto',marker_color=colors)]

		layout = go.Layout(
			title = "Comparaison de la variable {}".format(colonnes),
			xaxis=dict(
				title='{} du client contre la moyenne'.format(colonnes),
				),
			yaxis=dict(
				title=colonnes,
				)
		)
		fig1 = go.Figure(data = data, layout=layout)
		fig1.layout.template = "simple_white"
		#py.iplot(fig1)
		st.plotly_chart(fig1,use_container_width=True)

	with col2:
		st.subheader("Comparaison du client avec les clients ayant les mêmes profils.")
		cols1=["CODE_GENDER","OCCUPATION_TYPE","NAME_INCOME_TYPE","NAME_FAMILY_STATUS","NAME_EDUCATION_TYPE","NAME_TYPE_SUITE","NAME_HOUSING_TYPE"]
		colonnes1=st.selectbox("Selectionnez une Information", options=(cols1))
		age=round(df1.loc[a]['AGE'],2)
		df3=df1[df1['AGE']==age]
		#st.write(df3.head())

		temp = df3[colonnes1].value_counts()

		temp_val_y0 = []
		temp_val_y1 = []
		for val in temp.index:
			temp_val_y1.append(np.sum(df3['TARGET'][df3[colonnes1]==val] == 1))
			temp_val_y0.append(np.sum(df3['TARGET'][df3[colonnes1]==val] == 0))

		x2= temp.index
		y2=((temp_val_y1 / temp.sum()) * 100)
		y3=((temp_val_y0 / temp.sum()) * 100)
		data1 = [go.Bar(x = x2, y =y2 , name='Yes'),
				go.Bar(x = x2, y =y3 , name='No')]
		layout = go.Layout(
			title = "Comparaison du caractéristique {} en terme de remboursement de credit ou non en %".format(colonnes1),
			xaxis=dict(
				title='{} des demandeurs'.format(colonnes1),
				),
			yaxis=dict(
				title=colonnes1,
				)
		)
		fig2 = go.Figure(data = data1, layout=layout)
		fig2.layout.template = "plotly"
		#py.iplot(fig1)
		st.plotly_chart(fig2,use_container_width=True)

else:
	st.write("Cet identifiant n'est pas correcte")

#############################################
#age moyen des bons et mauvais emprunteurs
