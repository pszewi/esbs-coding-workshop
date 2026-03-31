import statsmodels.api as sm
import seaborn as sns 
import pandas as pd
import logging 

logger = logging.getLogger(__name__)


def run():
    df = pd.read_csv("demo-project/results/data_clean.csv")
    y = df['price']
    x = df[['rooms', 'area', 'floor']]

    x = sm.add_constant(x)
    model = sm.OLS(y, x)
    reg = model.fit()
    
    with open("demo-project/output/reg1.txt", "w") as file:
        file.write(str(reg.summary()))
        


    # plot the file and export 
    scatter = sns.scatterplot(
        data=df, x="area", y="price", hue='rooms',
        palette="muted"
    )
    fig = scatter.get_figure()
    fig.savefig("demo-project/output/out.png") 




# again the same principle for after development mode if finished, only executable code exists if we have an if statement
if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG, filename="demo-project/analysis.log")