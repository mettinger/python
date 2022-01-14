using Logging: global_logger
using TerminalLoggers: TerminalLogger
global_logger(TerminalLogger())

using DifferentialEquations
using Random
using Distributions
using SpecialPolynomials
using LinearAlgebra
using BenchmarkTools
using Plots
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

function kernelMatrixGet()
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

function sinDiffGet(theta)
    A = zeros(nOsc, nOsc)
    for i in 1:nOsc
        for j in i:nOsc
            A[i, j] = theta[i] - theta[j]
            A[j, i] = -A[i, j]
        end
    end
    A = sin(A)
    return A
end

function kuramoto2d!(du, u, p, t)

    #sinDiff = sinDiffGet(theta)
    #temp = W + dropdims(sum(sinDiff, dims = 2); dims=2)

    for i in 1:length(u)
        du[i] = W[i]
        for j in 1:length(u)
            du[i] = du[i] + ((K / nOsc) * p[1][i, j] * (sin(u[j] - u[i])))
        end
    end
end

########################

nOsc = 1000
upperTimeBound = 20.0
K = 0.01 * nOsc

benchmarkFlag = false
methodSwitch = 1
trivialKernel = true

##########################

# theta0, W are initial phase, intrinsic freq
theta0 = 2 * pi * rand(Float64, nOsc);
W = 0.5 * randn(Float64, nOsc);

if methodSwitch == 1
    method = Tsit5()
else
    method = RadauIIA5()
end

if trivialKernel
    kernelMatrix = ones((nOsc, nOsc))
else
    kernelMatrix = kernelMatrixGet()
end

prob = ODEProblem(kuramoto2d!, theta0, (0, upperTimeBound), [kernelMatrix]);

print("Solving...")

if benchmarkFlag
    @benchmark solve($prob, method = method, reltol = 1e-8, abstol = 1e-8, saveat = 0.1)
else
    sol = solve(prob, method = method, reltol = 1e-8, abstol = 1e-8, saveat = 0.1, progress = true, progress_steps = 5)
    print(sol.retcode)
end

time = sol.t
u = sol.u

odePhi = transpose(reduce(hcat, u))
orderParameterAbs = [abs(sum(exp.(odePhi[i, :] * (0 + 1im)))) for i in 1:length(time)]
plot(time, orderParameterAbs)

density(vec(W))

plot(cos.(theta0), sin.(theta0), seriestype = :scatter)

x = LinRange(-100, 100, 100)
y = [kernel(i) for i in x]
plot(x, y)

heatmap(kernelMatrix)


