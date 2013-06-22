'use strict';

//PhoneDetailCtrl.$inject = ['$scope', '$routeParams'];
function galleryCtrl($scope, $rootScope, $http) {

    $scope.pageSize = 4;
    $scope.startIndex = 0;
    $scope.currentCategory = "";
    $scope.categories = [];
    $scope.wordData = {};
    $rootScope.currentUser = {
        authenticated: false,
        username: "",
        email: "",
        firstName: ""
    };

    $scope.isSelected = function (category) {
        return $scope.currentCategory === category;
    };

    $scope.setCategory = function (category_name) {
        $scope.currentCategory = category_name;
        $scope.words = $scope.wordData[category_name];
    };

    $scope.forward = function () {
        $scope.startIndex += 1;
    };

    // FIXME: What does this function do? It appears to have no effect.
    $scope.hideBackButton = function () {
        $scope.startIndex < 1;
    };

    $scope.backward = function () {
        $scope.startIndex -= 1;
    };

    $http.get("/json/gallery_words/").success(function (data) {
        // Our initial currentCategory is whatever the first category is
        var firstItem = data[0];
        $scope.currentCategory = firstItem.category;
        $scope.words = firstItem.words;
        $scope.categories = [];
        for (var index in data) {
            var wordData = data[index];
            var categoryName = wordData.category;
            $scope.categories.push({
                name: categoryName
            });
            $scope.wordData[categoryName] = wordData.words;
        }
    });

    $http.get("/json/current_user/").success(function (data) {
        // Find out information about the currently-logged in user
        $rootScope.currentUser.authenticated = data["authenticated"];
        $rootScope.currentUser.username = data["username"]
        $rootScope.currentUser.email = data["email"]
        $rootScope.currentUser.firstName = data["first_name"]
    })
}

