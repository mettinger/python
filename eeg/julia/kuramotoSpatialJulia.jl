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

function kernelMatrixGet(nOsc)
    kernelMatrix = zeros(nOsc, nOsc)
    for i in 1:nOsc
        for j in i:nOsc
            r = distance(i, j)
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

    #=
    sinDiff = sin.(u .- u')
    du .= dropdims(W .+ sum(kernelMatrix .* sinDiff, dims=1)', dims=2)
    =#

    nOsc = length(W)
    for i in 1:nOsc
        du[i] = W[i]
        for j in 1:nOsc
            du[i] = du[i] + (kernelMatrix[i,j]) * sin(u[j] - u[i])
        end
    end
end

# ***************************************
##
const nOsc = 100
const upperTimeBound = 30
const K =  .014 * nOsc

const benchmarkFlag = false
const saveFlag = true
const plotFlag = true
const tsit5Flag = false 
const trivialKernel = true
const jacFlag = false
saveat = upperTimeBound/1000.

# ****************************************

# theta0, W are initial phase, intrinsic freq
Random.seed!(1234)
const theta0 = 2 * pi * rand(Float64, nOsc);
#const W = 0.5 * randn(Float64, nOsc);
const W = rand(Normal(5, 0.5), nOsc)

##
if tsit5Flag
    const method = Tsit5()
else
    #const method = RadauIIA5()
    const method = AutoTsit5(Rosenbrock23()) 
    #const method = lsoda()
end

if trivialKernel
    const kernelMatrix = (K/nOsc) * ones((nOsc, nOsc))
else
    const kernelMatrix = (K/nOsc) * kernelMatrixGet(nOsc)
end

if jacFlag
    const jac = jac!
else
    const jac = nothing
end

prob = ODEProblem(kuramoto2d!, theta0, (0, upperTimeBound), [kernelMatrix, W]);

##
println("Number of oscillators: " * string(nOsc))
println("Solving...")

if benchmarkFlag
    @btime sol = solve($prob, method = method, saveat = saveat, progress = true, progress_steps = 10, jac=jac)
else
    sol = solve(prob, method = method, reltol = 1e-8, abstol = 1e-8, saveat = saveat, progress = true, progress_steps = 10, jac=jac)
    print(sol.retcode)
end

if saveFlag
    df = DataFrame(sol)
    CSV.write("kuramoto_Out_" * Dates.format(now(),"mm-dd-HH-MM") * ".csv" , df)
end

##
if plotFlag
    t = sol.t
    u = sol.u
    odePhi = transpose(reduce(hcat, u))
    orderParameterAbs = [abs(sum(exp.(odePhi[i, :] * (0 + 1im)))) for i in 1:length(t)]
    display(PlotlyJS.plot(t, orderParameterAbs))
    #=
    display(PlotlyJS.plot(PlotlyJS.heatmap(z=kernelMatrix)))
    display(StatsPlots.density(vec(W)))
    display(PlotlyJS.plot(PlotlyJS.scatter(x=cos.(theta0), y=sin.(theta0), mode="markers")))
    =#
end
