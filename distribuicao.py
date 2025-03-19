#%%
import pandas as pd
import matplotlib.pyplot as plt



df = pd.read_csv("data/distribuicao-renda.csv", sep=";")
df20 = df[df["Ano-calendário"] == 2020]
df20br = df20[df20["Ente Federativo"] == "BRASIL"]


# Identify numerical columns for histograms
numerical_columns = df20br.select_dtypes(include=['float64', 'int64']).columns

# Create histograms for numerical columns
plt.figure(figsize=(15, 10))
for i, column in enumerate(numerical_columns, 1):
    plt.subplot(3, 3, i)
    df20br[column].hist(bins=20)
    plt.title(f'Histogram of {column}')
    plt.xlabel(column)
    plt.ylabel('Frequency')
    
    # Prevent overlapping
    plt.tight_layout()

# Save the plot
plt.savefig('histograms_2020_brazil.png')

# Optionally, print out the column names to verify
print("Numerical columns:", list(numerical_columns))