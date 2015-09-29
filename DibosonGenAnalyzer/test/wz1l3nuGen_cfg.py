import FWCore.ParameterSet.Config as cms
import GenNtuplizer.DibosonGenAnalyzer.ComLineArgs as ComLineArgs

process = cms.Process("WZGenAnalyze")

process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.load("GenNtuplizer.DibosonGenAnalyzer.genLeptons_cff")
process.load("GenNtuplizer.DibosonGenAnalyzer.genZCands_cff")
process.load("GenNtuplizer.DibosonGenAnalyzer.genJets_cff")
process.load("GenNtuplizer.DibosonGenAnalyzer.genNeutrinos_cff")
process.load("GenNtuplizer.DibosonGenAnalyzer.genWCands_cff")

options = ComLineArgs.getArgs()
genParticlesLabel = "genParticles" if not options.isMiniAOD else "prunedGenParticles"
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(options.inputFiles)
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(options.outputFile)
)

process.analyzeWZ = cms.EDAnalyzer("DibosonGenAnalyzer",
    jets = cms.InputTag("sortedJets"),
    leptons = cms.InputTag("sortedLeptons"),
    lheSource = cms.InputTag("externalLHEProducer" if options.isMiniAOD else "source"),
    zCands = cms.InputTag("trueZs"),
    wCands = cms.untracked.InputTag("sortedWCands"),
    nKeepZs = cms.untracked.uint32(3),
    nKeepLeps = cms.untracked.uint32(1),
    nKeepExtra = cms.untracked.uint32(1),
    extraName = cms.untracked.string("Nu" if not options.genMet else "genMET"),
    nKeepJets = cms.untracked.uint32(2),
    nKeepWs = cms.untracked.uint32(3),
    xSec = cms.untracked.double(options.crossSection)
)
process.p = cms.Path(process.selectLeptons * 
    process.selectNeutrinos * 
    process.selectZCands * 
    process.selectWCands *
    process.selectJets *
    process.analyzeWZ
)
