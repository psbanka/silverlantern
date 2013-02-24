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
 
angular.module('silver.filter', []);
 
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
var galleryCtrl = function($scope, greeter, user) {
    $scope.greeting = greeter.greet(user.name);

    $scope.categories = [
        {"name": "hipster", "class": "active"},
        {"name": "charming", "class": "notactive"},
        {"name": "brainiac", "class": "notactive"},
        {"name": "romantic", "class": "notactive"},
        {"name": "whimsical", "class": "notactive"}
    ];

    $scope.words = [
        {
            name: "abhorrent",
            info: "Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh,ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui."
        },
        {
            name: "abrasive",
            info: "Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh,ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui."
        },
        {
            name: "alluring",
            info: "Donec id elit non mi porta gravida at eget metus. Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh,ut fermentum massa justo sit amet risus. Etiam porta sem malesuada magna mollis euismod. Donec sed odio dui."
        }
    ];
};

