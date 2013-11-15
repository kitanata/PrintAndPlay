angular.module("app").controller('GamesController', function($scope, $location, GameResource) {
    $scope.games = GameResource.query();
    console.log($scope.games);
});
