'use strict';

/* App Module */

var myAppModule = angular.module('silver', ['silver.service', 'silver.directive', 'silver.filter']).
    config(function($interpolateProvider) {
        $interpolateProvider.startSymbol('{[{');
        $interpolateProvider.endSymbol('}]}');
    }).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: '/partials/front.html', controller: galleryCtrl}).
            when('/gallery', {templateUrl: '/partials/gallery.html', controller: galleryCtrl}).
            when('/study', {templateUrl: '/partials/study.html', controller: galleryCtrl}).
            otherwise({redirectTo: '/'});
    }]);

/*
    // A DJANGO-focused example
    config(['$routeProvider', function($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: 'views/main.html', controller: 'MainCtrl'}).
            when('/about', {templateUrl: 'views/about.html'}).
            when('/help', {templateUrl: 'views/help.html'}).
            when('/post/:id', {templateUrl: 'views/postRouter.html', controller: 'PostCtrl'}).
            otherwise({redirectTo: '/'});
    }])
*/
//when('/phones/:phoneId', {templateUrl: 'partials/phone-detail.html', controller: PhoneDetailCtrl}).
