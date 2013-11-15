angular.module("app").controller('RandomGameDetailController', function($scope, $route, GameResource) {
    $scope.game = GameResource.get({random:true});
    console.log($scope.game);
});
