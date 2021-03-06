var _ = require('lodash');
var fs = require('fs');
var babyparse = require('babyparse');
// var JSONStream = require('JSONStream');
// var es = require('event-stream');

var getSimilarities = function(splitType) {
  return {
      'human': require('./json/' + splitType + '/similarity-human-avg.json'),
      'multimodal_pool1': require('./json/' + splitType + '/similarity-' + splitType + '-multimodal_pool1-avg.json'),
      'multimodal_conv42': require('./json/' + splitType + '/similarity-' + splitType + '-multimodal_conv42-avg.json'),
      'multimodal_fc6': require('./json/' + splitType + '/similarity-' + splitType + '-multimodal_fc6-avg.json')
  };
};

var getCosts = function(name, splitType) {
  return require('./json/' + splitType + '/costs-' + name + '.json');
};

// If aggregate true, we only loop over coarse-grained sketch labels
var getPossibleSketches = function(data, config) {
  if(!config.aggregate) {
    return _.map(data, 'sketchLabel');
  } else {
    return _.uniq(_.map(data, function(d) {return config.conditionLookup[d.sketchLabel]}));
  }
};

var getConditionLookup = function(splitType) {
  return require('../bdaInput/' + splitType + '/condition-lookup.json');
};

function _logsumexp(a) {
  var m = Math.max.apply(null, a);
  var sum = 0;
  for (var i = 0; i < a.length; ++i) {
    sum += (a[i] === -Infinity ? 0 : Math.exp(a[i] - m));
  }
  return m + Math.log(sum);
}

// P(target | sketch) = e^{scale * sim(t, s)} / (\sum_{i} e^{scale * sim(t, s)})
// => log(p) = scale * sim(target, sketch) - log(\sum_{i} e^{scale * sim(t, s)})
var getL0score = function(target, sketch, context, params, config) {
  var similarities = config.similarities[params.perception];
  var scores = [];
  for(var i=0; i<context.length; i++){
    var similarity = (similarities[context[i]][sketch]); // transform to range from 0 to 1
    scores.push(params.simScaling * similarity);
  }
  var similarity = (similarities[target][sketch]);
  return params.simScaling * similarity - _logsumexp(scores);
};

// Interpolates between the 'informativity' term of S0 and S1 based on pragWeight param
// Try remapping these to [0,1]...
var informativity = function(targetObj, sketch, context, params, config) {
  var sim = config.similarities[params.perception];
  var S0inf = (sim[targetObj][sketch]);// + 1.001) / 2;
  var S1inf = getL0score(targetObj, sketch, context, params, config); //Math.exp()
  // console.log(targetObj);
  // console.log(sketch);
  // console.log(S1inf);
  return ((1 - params.pragWeight) * S0inf + params.pragWeight * S1inf);
};

// note using logsumexp here isn't strictly necessary, because all the scores
// are *negative* (informativity is log(p of listener)) and there aren't
// enough terms for precision to matter...
var getSpeakerScore = function(trueSketch, targetObj, context, params, config) {
  var possibleSketches = config.possibleSketches;
  var costw = params.costWeight;
  var infw = params.infWeight;
  var scores = [];
  // note: could memoize this for moderate optimization...
  // (only needs to be computed once per context per param, not for every sketch)
  for(var i=0; i<possibleSketches.length; i++){
    var sketch = possibleSketches[i];
    var inf = informativity(targetObj, sketch, context, params, config);
    var cost = config.costs[sketch];
    if (isNaN(cost)) {
      console.log(targetObj,sketch,context);
      console.log(cost);
    }
    // console.log(cost);
    var utility = infw * inf - costw * cost; // independent informativity weight parameter
    scores.push(utility);//Math.log(Math.max(utility, Number.EPSILON)));
  }
  var trueUtility = (infw * informativity(targetObj, trueSketch, context, params, config)
		     - costw * config.costs[trueSketch]);
  //var roundedUtility = Math.max(trueUtility, Number.EPSILON);
  // console.log(_logsumexp(scores))
  //console.log(params.alpha * Math.log(roundedUtility))// - _logsumexp(scores));
  return  trueUtility - _logsumexp(scores); // softmax subtraction bc log space,
};

function readCSV(filename){
  return babyparse.parse(fs.readFileSync(filename, 'utf8'),
			 {header:true, skipEmptyLines:true}).data;
};

function writeCSV(jsonCSV, filename){
  fs.writeFileSync(filename, babyparse.unparse(jsonCSV) + '\n');
}

function appendCSV(jsonCSV, filename){
  fs.appendFileSync(filename, babyparse.unparse(jsonCSV) + '\n');
}

function writeRow(row, filename){
  fs.writeFileSync(filename, row + '\n');
}
function appendRow(row, filename){
  fs.appendFileSync(filename, row + '\n');
}

var paramSupportWriter = function(i, s, p, handle) {
  var sLst = _.toPairs(s);
  var l = sLst.length;
  fs.writeSync(handle, i + ',' + sLst[0].join(',')+','+p+'\n');
};

var predictiveSupportWriter = function(s, filePrefix) {
  var dir = filePrefix.split('/').slice(0,3).join('/');
  if (!fs.existsSync(dir)){
      fs.mkdirSync(dir);
  }
  var predictiveFile = fs.openSync(filePrefix + "Predictives.csv", 'w');
    fs.writeSync(predictiveFile, [ "condition", 'game', "Target",
				"Distractor1", "Distractor2", "Distractor3",
				"TrueSketch", "PossibleSketch",
				"modelProb"] + '\n');

  var l = s.length;
  for (var i = 0; i < l; i++) {
    fs.writeSync(predictiveFile, s[i] + '\n');
  }

  fs.closeSync(predictiveFile);
};

// Note this is highly specific to a single type of erp
var bayesianErpWriter = function(erp, filePrefix) {
  var supp = erp.support();

  if(_.has(supp[0], 'params')) {
    var paramFile = fs.openSync(filePrefix + "Params.csv", 'w');
    fs.writeSync(paramFile, ["id", "perception", "pragmatics","production",
			     "simScaling", "pragWeight","costWeight","infWeight",
			     "logLikelihood", "posteriorProb"] + '\n');
  }

  supp.forEach(function(s, index) {
    if(_.has(s, 'params')) {
      paramSupportWriter(index, s.params, erp.score(s), paramFile);
    }
  });
    if(_.has(supp[0], 'params')) {
    fs.closeSync(paramFile);
  }
  console.log('writing complete.');
};

var getSubset = function(data, properties) {
  var matchProps = _.matches(properties);
  return _.filter(data, matchProps);
};

var locParse = function(filename) {
  return babyparse.parse(fs.readFileSync(filename, 'utf8'),
       {header: true,
        skipEmptyLines : true}).data;
};

module.exports = {
  getSimilarities, getPossibleSketches, getCosts, getSubset, getConditionLookup,
  writeRow, appendRow,
  predictiveSupportWriter,
  getL0score, getSpeakerScore,
  bayesianErpWriter, writeCSV, readCSV, locParse
};
