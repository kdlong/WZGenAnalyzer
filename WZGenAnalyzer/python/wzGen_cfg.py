import FWCore.ParameterSet.Config as cms

process = cms.Process("WZGenAnalyze")

# parse variables from cmsRun
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('analysis')

options.inputFiles = "file:/afs/cern.ch/user/k/kelong/work/WZ_MCAnalysis/POWHEG_WZ/WZ_powheg_pythia8_CUETP8M1_10E5ev.root"
options.outputFile = ""
options.maxEvents = -1

options.parseArguments() 

process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(options.maxEvents))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(options.inputFiles)
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string(options.outputFile)
)

process.selectedGenParticles = cms.EDFilter("CandViewShallowCloneProducer",
    src = cms.InputTag("genParticles"),
    cut = cms.string("pt > 10 && abs(eta) < 2.4")                           
)

process.leptons = cms.EDFilter("PdgIdAndStatusCandSelector",
                           src = cms.InputTag("selectedGenParticles"),
                           pdgId = cms.vint32( 11, 13 ),
                           status = cms.vint32( 1 )                          
)

process.sortedLeptons = cms.EDFilter("LargestPtCandSelector",
    src = cms.InputTag("leptons"),
    maxNumber = cms.uint32(10)
)

process.muons = cms.EDFilter("PdgIdAndStatusCandSelector",
    src = cms.InputTag("selectedGenParticles"),
    pdgId = cms.vint32( 13 ),
    status = cms.vint32( 1 )                          
)

process.electrons = cms.EDFilter("PdgIdAndStatusCandSelector",
    src = cms.InputTag("selectedGenParticles"),
    pdgId = cms.vint32( 11 ),
    status = cms.vint32( 1 )                          
)

process.zMuMuCands = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string('muons@+ muons@-'),
    cut = cms.string('30 < mass < 250'),
)

process.zeeCands = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string('electrons@+ electrons@-'),
    cut = cms.string('30 < mass < 250'),
)

process.sortedZeeCands = cms.EDFilter("BestZCandSelector",
    src = cms.InputTag("zeeCands"),
    maxNumber = cms.uint32(1)
)

process.sortedZMuMuCands = cms.EDFilter("BestZCandSelector",
    src = cms.InputTag("zMuMuCands"),
    maxNumber = cms.uint32(1)
)
import RecoJets.Configuration.GenJetParticles_cff as GenJetParticles

process.genParticlesForJets = GenJetParticles.genParticlesForJets
process.genParticlesForJetsNoNu = GenJetParticles.genParticlesForJetsNoNu
import RecoJets.Configuration.RecoGenJets_cff as RecoGenJets
process.ak4GenJetsNoNu = RecoGenJets.ak4GenJetsNoNu
#process.deltaRCutJets = cms.EDFilter( "DeltaROverlapExclusionSelector",
#    src = cms.InputTag("jets"),
#    overlap = cms.InputTag("leptons"),
#    maxDeltaR = cms.double(0.5),
#)

process.selectedJets = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag("ak4GenJetsNoNu"),
    ptMin   = cms.double(30),
    etaMin = cms.double(-4.7),
    etaMax = cms.double(4.7)
)

process.sortedJets = cms.EDFilter("LargestPtCandSelector",
    src = cms.InputTag("selectedJets"),
    maxNumber = cms.uint32(20)
)

process.analyzeWZ = cms.EDAnalyzer("WZGenAnalyzer",
    jets = cms.InputTag("sortedJets"),
    leptons = cms.InputTag("sortedLeptons"),
    zMuMuCands = cms.InputTag("zMuMuCands"),
    zeeCands = cms.InputTag("zeeCands"),
    nKeepLeps = cms.untracked.uint32(3)
)

process.p = cms.Path(((process.selectedGenParticles*process.leptons*process.sortedLeptons)+ 
    ((process.muons*process.zMuMuCands) + (process.electrons*process.zeeCands)) +
    (process.genParticlesForJets*process.genParticlesForJetsNoNu*process.ak4GenJetsNoNu)*
    (process.selectedJets*process.sortedJets)) *
    (process.sortedZMuMuCands + process.sortedZeeCands) * 
    process.analyzeWZ
)
