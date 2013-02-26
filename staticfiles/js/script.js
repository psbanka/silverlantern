angular.module('silverlantern.service', []).
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

angular.module('silverlantern.directive', []).
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

angular.module('silverlantern.filter', []);

myAppModule = angular.module('silverlantern', ['silverlantern.service', 'silverlantern.directive', 'silverlantern.filter']).
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
};
