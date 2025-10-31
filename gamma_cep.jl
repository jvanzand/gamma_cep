using Octofitter
using OctofitterRadialVelocity
using PlanetOrbits
using CairoMakie
using PairPlots
using CSV
using DataFrames
using Distributions
using Infiltrator


println("Number of threads: ", Threads.nthreads(), ", as specified in ~/.bashrc")

do_rv=true
if do_rv
    rv_file = "data/octofitter_all_rvs.csv"
    rv_dat_raw = CSV.read(rv_file, DataFrame, delim=',')
    rv_dat = DataFrame();
    rv_dat.epoch = jd2mjd.(rv_dat_raw.time)
    rv_dat.rv = rv_dat_raw.mnvel
    rv_dat.σ_rv = rv_dat_raw.errvel
    # tels = sort(unique(rv_dat_raw.tel))


    ## One likelihood for each instrument
    rvlike_apf = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "apf",:],
        name="APF",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.jump_offset
            jitter ~ LogUniform(0.1,30) # m/s
            #trend_slope = system.my_slope # m/s/day #system.my_little_slope
        end
    )

    rvlike_hires = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "j",:],
        name="HIRES",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.jump_offset
            jitter ~ LogUniform(0.1,30) # m/s
            #trend_slope = system.my_slope
        end
    )

    rvlike_mcdonald1 = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "mcdonald1",:],
        name="McDonald1",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.mcdonald1_offset
            jitter ~ LogUniform(0.1,100) # m/s
            #trend_slope = system.my_slope
        end
    )

    rvlike_mcdonald2 = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "mcdonald2",:],
        name="McDonald2",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.mcdonald2_offset
            jitter ~ LogUniform(0.1,100) # m/s
            #trend_slope = system.my_slope
        end
    )

    rvlike_mcdonald3 = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "mcdonald3",:],
        name="McDonald3",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.mcdonald2_offset
            jitter ~ LogUniform(0.1,40) # m/s
            #trend_slope = system.my_slope
        end
    )

    rvlike_cfht = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "cfht",:],
        name="CFHT",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.mcdonald2_offset
            jitter ~ LogUniform(0.1,30) # m/s
            #trend_slope = system.my_slope
        end
    )

    rvlike_torres = StarAbsoluteRVLikelihood(
        rv_dat[rv_dat_raw.tel .== "torres",:],
        name="Torres+07",
        #trend_function = (θ_obs, epoch) -> θ_obs.trend_slope * (epoch - 57229.16),  # Linear trend
        variables=@variables begin
            offset ~ Uniform(-100000,100000) # = system.mcdonald2_offset
            jitter ~ LogUniform(0.1,30) # m/s
            #trend_slope = system.my_slope
        end
    )
    # @infiltrate

    rvlikelihoods = []
    push!(rvlikelihoods, rvlike_apf)
    push!(rvlikelihoods, rvlike_hires)
    push!(rvlikelihoods, rvlike_mcdonald1)
    push!(rvlikelihoods, rvlike_mcdonald2)
    push!(rvlikelihoods, rvlike_mcdonald3)
    push!(rvlikelihoods, rvlike_cfht)
    # push!(rvlikelihoods, rvlike_torres)
end

do_astrom=true
if do_astrom
    relAst_file = "data/octofitter_all_relAst.csv"
    relAst_dat_raw = CSV.read(relAst_file, DataFrame, delim=',')
    relAst_dat = DataFrame();
    relAst_dat.epoch = jd2mjd.(relAst_dat_raw.jd)
    relAst_dat.sep =    relAst_dat_raw.sep_mas
    relAst_dat.σ_sep =  relAst_dat_raw.err_sep_mas
    relAst_dat.pa =     relAst_dat_raw.PA_rad
    relAst_dat.σ_pa =   relAst_dat_raw.err_PA_rad


    astrom_like_subaru = PlanetRelAstromLikelihood(
        relAst_dat[relAst_dat_raw.Inst .== "Subaru_CIAO",:],
        name = "Subaru_CIAO",
        variables = @variables begin
            jitter ~ LogUniform(0.1, 10) # mas [optional]
            #northangle ~ Normal(0, deg2rad(1)) # radians of offset [optional]
            #platescale ~ truncated(Normal(1, 0.01), lower=0) # 1% relative platescale uncertainty
        end
    )

    astrom_like_CAomega = PlanetRelAstromLikelihood(
        relAst_dat[relAst_dat_raw.Inst .== "CA_omega",:],
        name = "CA_omega",
        variables = @variables begin
            jitter ~ LogUniform(0.1, 10) # mas [optional]
            #northangle ~ Normal(0, deg2rad(1)) # radians of offset [optional]
            #platescale ~ truncated(Normal(1, 0.01), lower=0) # 1% relative platescale uncertainty
        end
    )

    astrom_like_unknown = PlanetRelAstromLikelihood(
        relAst_dat[relAst_dat_raw.Inst .== "unknown",:],
        name = "unknown",
        variables = @variables begin
            jitter ~ LogUniform(0.1, 20) # mas [optional]
            #northangle ~ Normal(0, deg2rad(1)) # radians of offset [optional]
            #platescale ~ truncated(Normal(1, 0.01), lower=0) # 1% relative platescale uncertainty
        end
    )

    astrom_like_astralux = PlanetRelAstromLikelihood(
        relAst_dat[relAst_dat_raw.Inst .== "AstraLux",:],
        name = "AstraLux",
        variables = @variables begin
            jitter ~ LogUniform(0.1, 10) # mas [optional]
            #northangle ~ Normal(0, deg2rad(1)) # radians of offset [optional]
            #platescale ~ truncated(Normal(1, 0.01), lower=0) # 1% relative platescale uncertainty
        end
    )

    relAstlikelihoods = []
    push!(relAstlikelihoods, astrom_like_subaru)
    push!(relAstlikelihoods, astrom_like_CAomega)
    push!(relAstlikelihoods, astrom_like_unknown)
    push!(relAstlikelihoods, astrom_like_astralux)
end

###################################################
## Define the companions. One is actually a star
## I CANNOT use the posteriors found by Knudstrup+2023 as priors, because
## derived those posteriors using the same data I'm using here


planet_1 = Planet(
    name="B",
    basis=Visual{KepOrbit},#RadialVelocityOrbit,
    likelihoods=relAstlikelihoods,
    variables=@variables begin
        
        mass = system.M_sec # minimum planet mass [jupiter masses]. really m*sin(i)
        M = system.M # Total mass of the system, which includes primary and secondary (planet is ~0)
        
        e ~ Uniform(0, 0.5)
        ω ~ UniformCircular(0)
        a ~ LogUniform(10, 100)
        θ ~ UniformCircular(2.2)
        tp = θ_at_epoch_to_tperi(θ, 48903; M, e, a, i, ω, Ω)#48903 # reference epoch for τ. Choose an MJD date near your data.

        ## 3D orbital parameters
        plx = system.plx
        i ~ Sine() # Uninformative, but remember Reffert+Quirrenbach got inc. from Hipparcos
        Ω ~ UniformCircular()
    end
)

planet_2 = Planet(
    name="Ab", # This is the actual planet
    basis=Visual{KepOrbit},#RadialVelocityOrbit,
    likelihoods=[], # No likelihood specifically for this obj. The RV data belongs to the primary
    variables=@variables begin
        
        M = system.M_pri # Just the mass of A, bc that's Ab's primary (and the planet mass is negligible)
        mass ~ LogUniform(0.01, 80) # =1.41 # Wide range for Ab to see if Octofitter can fit it. minimum planet mass [jupiter masses]. really m*sin(i)
        
        e ~ Uniform(0, 0.5)
        ω ~ UniformCircular(1)
        a ~ LogUniform(1, 5)
        θ ~ UniformCircular(5.2)
        tp = θ_at_epoch_to_tperi(θ, 48903; M, e, a, i, ω, Ω) # reference epoch for τ. This is the median MJD of my RV data

        ## 3D orbital parameters
        plx = system.plx
        i ~ Sine()
        Ω ~ UniformCircular()
    end
)

## HGCA likelihood using DR3 ID. Use instantaneous option bc the companion period is ~80 yr
# hgca_like = HGCAInstantaneousLikelihood(gaia_id=2281778105594488192)

# hgca_like = HGCALikelihood(
#     gaia_id=2281778105594488192,
#     variables=@variables begin
#     end
# )
hgca_like = HGCAInstantaneousLikelihood(gaia_id=2281778105594488192, N_ave=1)

system_likes = push!(rvlikelihoods, hgca_like)

sys = System(
    name = "HD222404",
    companions=[planet_1, planet_2],
    likelihoods=[rvlike_cfht, rvlike_hires, rvlike_apf,
                 rvlike_mcdonald1, rvlike_mcdonald2, rvlike_mcdonald3],
    variables=@variables begin
        #M ~ truncated(Normal(1.27, 0.06),lower=1.09, upper=1.45)
        plx ~ gaia_plx(gaia_id=2281778105594488192)
        
        M_pri ~ truncated(Normal(1.27, 0.06),lower=1.09, upper=1.45) # Msol
        M_sec ~ LogUniform(100, 1000)  # MJup
        M = M_pri + M_sec*Octofitter.mjup2msol # Msol
        
        # Priors on the center of mass proper motion (mas/yr)
        pmra =-64.86018#~ Normal(-64.86, 10)
        pmdec =171.15860#~ Normal(171.16,  10)
    end
)



#################################################################
# Now make the model and sample, or load a pre-computed chain
model = Octofitter.LogDensityModel(sys)

load_chain=false
if load_chain
    load_folder="outputs_McD3_full/"
    chain = Octofitter.loadchain(load_folder+"output.fits")
    model = deserialize(load_folder+"model.jls")
    fig_rv_post = Octofitter.rvpostplot(model, chain)
    octoplot(model, chain)
    fig_corner = octocorner(model, chain)

else

    using_pma = true
    if using_pma
        using Pigeons
        chain, pt = octofit_pigeons(model, n_rounds=13, explorer=SliceSampler())
        octoplot(model, chain)
        Octofitter.rvpostplot(model, chain)
        fig_corner = octocorner(model, chain)
        # display(chain_pma)

        # @infiltrate
    
    else

        init_chain = initialize!(model)

        # Plot initialized data
        if do_rv
            fig_rv_init = Octofitter.rvpostplot(model, init_chain)
        end

        # if do_astrom
        #     fig_relAstr_init = octoplot(model, init_chain)
        # end


        ## Normal Octofit sampling
        using Random
        rng = Random.Xoshiro(0)

        chain = octofit(rng, model, iterations=1000)


        # Make RV plots
        if do_rv
            fig_rv_post = Octofitter.rvpostplot(model, chain)
        end

        # Make RelAstro plots
        if do_astrom
            octoplot(model, chain)
        end

        fig_corner = octocorner(model, chain)
    end

    # Save chain
    Octofitter.savechain("output.fits", chain)
    
    # Save model
    serialize("model.jls", model)

end

lines(
    chain["Ab_e"][:],
    axis=(;
        xlabel="iteration",
        ylabel="semi-major axis (AU)"
    )
)


