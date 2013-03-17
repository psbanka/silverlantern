'use strict';

//PhoneDetailCtrl.$inject = ['$scope', '$routeParams'];
function galleryCtrl($scope, $http) {

    $scope.pageSize = 4;
    $scope.startIndex = 0;
    $scope.current_category = "";
    $scope.categories = [];
    $scope.wordData = {};

    $scope.isSelected = function(category) {
        return $scope.current_category === category;
    };
    $scope.setCategory = function(category_name) {
        $scope.current_category = category_name;
        $scope.words = $scope.wordData[category_name];
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

    $http.get('/json/gallery_words/').success(function(data) {
        // Our initial current_category is whatever the first category is
        $scope.current_category = data[0]["category"];
        $scope.words = data[0]["words"];
        $scope.categories = [];
        for (var index in data) {
            var categoryName = data[index]["category"];
            $scope.categories.push({
                name: categoryName
            });
            $scope.wordData[categoryName] = data[index]["words"];
        }
    });
}

