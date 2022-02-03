##
using Logging: global_logger
using TerminalLoggers: TerminalLogger
global_logger(TerminalLogger())

using DifferentialEquations
using LSODA
using Random
using Distributions
using SpecialPolynomials
using LinearAlgebra
using BenchmarkTools
using DataFrames
using CSV
using Dates
using PlotlyJS
using StatsPlots

##
function orderParameterGet(phaseVector)
    return abs(sum(exp.(phaseVector * (0 + 1im))))
end

function kernel(r)
    scale = 10
    amplitudeMultiple = 2

    r = r / scale
    p = basis(Hermite, 4)
    return amplitudeMultiple * 0.25 * p(r / sqrt(2)) * pdf(Normal(), r)
end

function indexToCoord(i)
    i = i - 1
    nOneDimension = Int(sqrt(nOsc))
    x = mod(i, nOneDimension)
    y = Int(floor(i / nOneDimension))
    return [x, y]
end

function distance(x0, x1)
    coord0 = indexToCoord(x0)
    coord1 = indexToCoord(x1)
    return norm(coord0 - coord1)
end

function distanceMatrixGet(nOsc)
    distanceMatrix = zeros(Float64, nOsc, nOsc)
    for i in 1:nOsc
        for j in i:nOsc
            distanceMatrix[i,j] = distance(i, j)
            distanceMatrix[j,i] = distanceMatrix[i,j]
        end
    end
    return distanceMatrix
end

function kernelMatrixGet(distanceMatrix)
    nOsc = size(distanceMatrix)[1]
    kernelMatrix = zeros(nOsc, nOsc)
    for i in 1:nOsc
        for j in i:nOsc
            r = distanceMatrix[i,j]
            kernelMatrix[i, j] = kernel(r)
            kernelMatrix[j, i] = kernelMatrix[i, j]
        end
    end
    return kernelMatrix
end

function jac!(J, u, p, t)

    kernelMatrix, W = p
    cosDiff = cos.(u .- u')

    J .= zeros(nOsc, nOsc)

    for i in 1:nOsc
        for j in 1:nOsc
            J[i,j] = kernelMatrix[i,j] * mean(cosDiff[:,j]) * (-1)^(i == j)
        end
    end
end

function kuramoto2d!(du, u, p, t)

    kernelMatrix, W = p

    nOsc = length(W)
    for i in 1:nOsc
        du[i] = W[i]
        for j in 1:nOsc
            du[i] = du[i] + (kernelMatrix[i,j]) * sin(u[j] - u[i])
        end
    end
end

# PARAMETERS TO SET

##
const kernelSwitch = 0
if kernelSwitch == 0
    const nOsc = 1024 # should be perfect square
    const K = 4
    const kernelMatrix = (K/nOsc) * ones((nOsc, nOsc))
elseif kernelSwitch == 1
    const nOsc = 1024 # should be perfect square
    const K = 4 
    const distanceMatrix = distanceMatrixGet(nOsc)
    const kernelMatrix = (K/nOsc) * kernelMatrixGet(distanceMatrix)
elseif kernelSwitch == 2
    const distanceMatrix = Matrix{Float64}(DataFrame(CSV.File("distanceMatrix.csv", header=false)))
    const nOsc = size(distanceMatrix)[1]
    const K = K_nOsc_Ratio * nOsc
    const kernelMatrix = (K/nOsc) * kernelMatrixGet(distanceMatrix)
end

const distributionSwitch = 1
const upperTimeBound = 100

const saveFlag = true
const plotFlag = true
const tsit5Flag = false 
const jacFlag = false
saveat = upperTimeBound/1000.

# PARAMETERS END 

##
if tsit5Flag
    const method = Tsit5()
else
    const method = AutoTsit5(Rosenbrock23()) 
    #const method = lsoda()
end

if jacFlag
    const jac = jac!
else
    const jac = nothing
end

# theta0, W are initial phase, intrinsic freq
Random.seed!(1234)
const theta0 = 2 * pi * rand(Float64, nOsc);

if distributionSwitch == 0
    const probabilityDistribution = Cauchy(0,1)
    const distributionTitle = string(probabilityDistribution)
elseif distributionSwitch == 1
    const probabilityDistribution = MixtureModel([Normal(-2.0, 1.0), Normal(2.0, 1.0)])
    const distributionTitle = string(probabilityDistribution.components) * "<br>" * string(probabilityDistribution.prior)
elseif distributionSwitch == 2
    const probabilityDistribution = Exponential(2.5)
    const distributionTitle = string(probabilityDistribution)
elseif distributionSwitch == 3
    const probabilityDistribution = MixtureModel([Exponential(2), Normal(5., .5), Normal(7., .5)], [.9,.05,.05])
    const distributionTitle = string(probabilityDistribution)
end

const W = rand(probabilityDistribution, nOsc) 
display(StatsPlots.density(vec(W)))

##
println("Number of oscillators: " * string(nOsc))
println("K: " * string(K))
println("Natural frequencies: " * string(probabilityDistribution))
println("Solving...")

prob = ODEProblem(kuramoto2d!, theta0, (0, upperTimeBound), [kernelMatrix, W]);
sol = solve(prob, method = method, reltol = 1e-8, abstol = 1e-8, saveat = saveat, progress = true, progress_steps = 10, jac=jac)
print(sol.retcode)

if saveFlag
    df = DataFrame(sol)
    CSV.write("kuramoto_Out_" * Dates.format(now(),"mm-dd-HH-MM") * ".csv" , df)
end

##
if plotFlag
    t = sol.t
    u = sol.u
    odePhi = transpose(reduce(hcat, u))
    orderParameterAbs = [orderParameterGet(odePhi[i,:]) for i in 1:length(t)]
    layout = Layout(title="nOsc: " * string(nOsc) * "<br>K: " * string(K) * "<br>" * distributionTitle)
    display(PlotlyJS.plot(t, orderParameterAbs, layout))
    
    #display(PlotlyJS.plot(PlotlyJS.scatter(x=cos.(odePhi[1000,:]), y=sin.(odePhi[1000,:]), mode="markers")))
    #display(PlotlyJS.plot(PlotlyJS.heatmap(z=kernelMatrix)))
    #display(PlotlyJS.plot(PlotlyJS.scatter(x=cos.(theta0), y=sin.(theta0), mode="markers")))
    
end
