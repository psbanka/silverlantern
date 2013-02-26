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
 
angular.module('silver.directive', []).
  directive('fadey', function() {
    return {
      restrict: 'A',
      link: function(scope, elm, attrs) {
        var duration = parseInt(attrs.fadey, 10);
        if (isNaN(duration)) {
          duration = 500;
        }
        elm = jQuery(elm);
        elm.hide();
        elm.fadeIn(duration);

        scope.destroy = function(complete) {
          elm.fadeOut(duration, function() {
            if (complete) {
              complete.apply(scope);
            }
          });
        };
      }
    };
  });

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

    $scope.pageSize = 4;
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

    /* This section would be used if we added and removed items from
     * The list instead of simply changing the indexes around display.
    $scope.clearItem = function(item) {
        var idx = $scope.items.indexOf(item);
        if (idx !== -1) {
            //injected into repeater scope by fadey directive
            this.destroy(function() {
                $scope.items.splice(idx, 1);
            });
        }
    };
    */

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

