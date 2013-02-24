angular.module('silver.service', []).
  value('greeter', {
    salutation: 'Hello',
    localize: function(localization) {
      this.salutation = localization.salutation;
    },
    greet: function(name) {
      return this.salutation + ' ' + name + '!';
    }
  }).
  value('user', {
    load: function(name) {
      this.name = name;
    }
  });
 
angular.module('silver.directive', []);
 
angular.module('silver.filter', []).
  filter('startFrom', function() {
    return function(input, start) {
        if (input === undefined) {
            return input;
        }
        start = +start; //parse to int
        return input.slice(start);
    };
  });
 
myAppModule = angular.module('silver', ['silver.service', 'silver.directive', 'silver.filter']).
  run(function(greeter, user) {
    // This is effectively part of the main method initialization code
    greeter.localize({
      salutation: 'Bonjour'
    });
    user.load('World');
  }).
  config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
  });

// A Controller for your app
var galleryCtrl = function($scope, $http) {

    $scope.pageSize = 3;
    $scope.startIndex = 0;

    $scope.current_category = "hipster";

    $scope.isSelected = function(category) {
        return $scope.current_category === category;
    };

    $scope.setCategory = function(category_name) {
        $scope.current_category = category_name;
        $http.get('/json/gallery_words/' + $scope.current_category).success(function(data) {
            $scope.words = data;
        });
    };

    $scope.forward = function() {
        $scope.startIndex += 1;
    };

    $scope.hideBackButton = function() {
        $scope.startIndex < 1;
    };

    $scope.backward = function() {
        $scope.startIndex -= 1;
    };

    $http.get('/json/gallery_categories/').success(function(data) {
        $scope.categories = data;
    });

    $http.get('/json/gallery_words/' + $scope.current_category).success(function(data) {
        $scope.words = data;
    });
};

