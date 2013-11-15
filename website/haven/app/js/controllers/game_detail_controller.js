angular.module("app").controller('GameDetailController', function($scope, $route, GameResource) {
    id = $route.current.params.gameId
    $scope.game = GameResource.get({gameId:id});
    console.log($scope.game);
});
