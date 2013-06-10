'use strict';

/* App Module */

var myAppModule = angular.module('silver', ['silver.service', 'silver.directive', 'silver.filter']).
    config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
    }).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {
                controller: galleryCtrl,
                templateUrl: '/partials/front.html'
            }).
            when('/foo', {
                controller: galleryCtrl,
                templateUrl: '/partials/foo.html'
            }).
            when('/gallery', {
                controller: galleryCtrl,
                templateUrl: '/partials/gallery.html'
            }).
            when('/study', {
                controller: galleryCtrl,
                templateUrl: '/partials/study.html'
            }).
            otherwise({redirectTo: '/'});
    }]);
