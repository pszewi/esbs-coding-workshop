import statsmodels.api as sm
import seaborn as sns
import pandas as pd
import logging

# again, dev mode logging (if even needed, only if you want to actually log problems)
# logger = logging.getLogger(__name__)
# logging.basicConfig(...)

# change the relative path when running with python
df = pd.read_csv("../../demo-project/results/data_clean.csv")
y = df['price']
x = df[['rooms', 'area', 'floor']]

x = sm.add_constant(x)
model = sm.OLS(y, x)
reg = model.fit()
print(reg.summary())

# plot the file and export 
scatter = sns.scatterplot(
    data=df, x="area", y="price", hue='rooms',
    palette="muted"
)
fig = scatter.get_figure()
fig.savefig("demo-project/output/out.png") 


# TODO: move on to new features/re-running on different data/packaging
