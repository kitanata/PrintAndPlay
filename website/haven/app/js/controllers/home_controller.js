angular.module("app").controller('HomeController', function($scope, $location, GameResource) {
  $scope.games = GameResource.query({limit:12});
});
