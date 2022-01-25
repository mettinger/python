##
using CSV
using DataFrames
using PlotlyJS

##
df = DataFrame(CSV.File("kuramoto.csv"))

##
data = Matrix(df)

##
index = 100
img = reshape(copy(data[index,2:end]), (128,128))

plot(heatmap(z=img))
