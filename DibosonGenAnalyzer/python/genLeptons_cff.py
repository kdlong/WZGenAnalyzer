import FWCore.ParameterSet.Config as cms
import GenNtuplizer.DibosonGenAnalyzer.ComLineArgs as ComLineArgs

options = ComLineArgs.getArgs()
genParticlesLabel = "genParticles" if not options.isMiniAOD else "prunedGenParticles"

selectedElectrons = cms.EDFilter("GenParticleSelector",
    src = cms.InputTag(genParticlesLabel),
    cut = cms.string("abs(pdgId) == 11 && %s" %
        ("fromHardProcessFinalState" if not options.isHardProcess else "isHardProcess()")) #"statusFlags().fromHardProcessBeforeFSR()"))  
)
selectedMuons = cms.EDFilter("GenParticleSelector",
    src = cms.InputTag(genParticlesLabel),
    cut = cms.string("abs(pdgId) == 13 && %s" % 
        ("fromHardProcessFinalState" if not options.isHardProcess else "isHardProcess()")) #"statusFlags().fromHardProcessBeforeFSR()"))  
)

radiatedElectrons = cms.EDFilter("GenParticleSelector",
    src = cms.InputTag(genParticlesLabel),
    cut = cms.string("abs(pdgId) == 11 && isPromptFinalState()")
)

radiatedMuons = cms.EDFilter("GenParticleSelector",
    src = cms.InputTag(genParticlesLabel),
    cut = cms.string("abs(pdgId) == 13 && isPromptFinalState()")
)
if options.includeTaus:
    selectedTaus = cms.EDFilter("GenParticleSelector",
        src = cms.InputTag(genParticlesLabel),
        cut = cms.string("abs(pdgId) == 15 && %s" %
            ("statusFlags().fromHardProcess && isLastCopy" if not options.isHardProcess else "isHardProcess()"))  
    )

leps = cms.EDProducer("CandViewMerger",
    src = cms.VInputTag("selectedElectrons", "selectedMuons")
) if not options.includeTaus else cms.EDProducer("CandViewMerger",
    src = cms.VInputTag("selectedElectrons", 
        "selectedMuons",
        "selectedTaus"
    )
)
selectLeptons = cms.Sequence(
    (selectedMuons + selectedElectrons) if not options.includeTaus else
    (selectedMuons + selectedElectrons + selectedTaus)
)

if options.includeRadiated:
    radiatedLeptons = cms.EDProducer("CandViewMerger",
        src = cms.VInputTag("radiatedElectrons", "radiatedMuons")
    )
    leptons = cms.EDProducer("CandViewMerger",
        src = cms.VInputTag("radiatedLeptons", "leps")
    )
    selectLeptons += ((radiatedMuons + radiatedElectrons)*radiatedLeptons)
else:
    leptons = leps
sortedLeptons = cms.EDFilter("LargestPtCandSelector",
    src = cms.InputTag("leptons"),
    maxNumber = cms.uint32(10)
)
selectLeptons += cms.Sequence(leps*leptons*sortedLeptons)
