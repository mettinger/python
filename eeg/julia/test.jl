using DifferentialEquations
using Random

function test_1!(du, u, p, t)
    W = p[1]

    du .= W
end

function test_2!(du, u, p, t)
    W = p[1]

    for i in 1:length(W)
        du[i] = W[i]
    end
end

# for reproducibility
Random.seed!(1234);

nOsc = 5
theta0 = 2 * pi * rand(Float64, nOsc);
W = 0.5 * randn(Float64, nOsc);

prob = ODEProblem(test_1!, theta0, (0, 20), [W]); # doesn't work.  sol.u is constant
#prob = ODEProblem(test_2!, theta0, (0, 20), [W]); # works!  
sol = solve(prob)

