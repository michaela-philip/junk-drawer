import pandas as pd
from pathlib import Path


def main():
    #List to store dataframes
    fileData = []
    #Path to panjiva data files directory/folder
    directory = '/Users/qianqiantang/Desktop/panjiva-code-main/data_for_paper'
    #To read existing files in the folder
    files = Path(directory).glob('*.txt')
    #For each file in the folder
    for file in files:

        file = 'data/input/usa_00004.dat.gz'
        print(file)
        #Read the file, name columns, and append to the masterList
        with file.open(encoding='utf-8', errors='ignore') as f:
            string_data = f.readline()
            #Split rows by #@#@# and columns by '~'
            df = pd.DataFrame([x.split("'~'") for x in string_data.split('#@#@#')])
            #print the file name which is being read
            print(f"Number of columns in the DataFrame: {df.shape[1]}")

            #Add column names to the dataframe
            df.columns = ['column names here']
            #Drop columns that won't be necessary for matching with y_14 data
            df.drop(columns= ['drop columns which you dont need'], inplace=True)
            #Turn specific columns into numeric type
            #df[["weightKg", "weightT","volumeTEU","valueOfGoodsUSD","numberOfContainers","FROB","hasLCL"]] = df[["weightKg", "weightT","volumeTEU","valueOfGoodsUSD", "numberOfContainers","FROB","hasLCL"]].apply(pd.to_numeric)
            fileData.append(df)
    masterList = pd.concat(fileData)
    #you can drop duplicated items if you want
    masterList.drop_duplicates(inplace=True)
    #Save masterList as excel file
    #masterList.to_excel('~/Documents/PycharmProjects/Panjiva/PanjivaUSImportsMasterList.xlsx')
    #Save masterList as Stata data file
    masterList.to_stata('/Users/qianqiantang/Desktop/panjiva-code-main/PanjivaUSImports.dta', version = 118)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()