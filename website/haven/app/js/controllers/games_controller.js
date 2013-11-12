angular.module("app").controller('GamesController', function($scope, $location, AuthenticationService) {
  $scope.title = "Games";
  $scope.message = "Mouse Over these images to see a directive at work";

  var onLogoutSuccess = function(response) {
    $location.path('/login');
  };

  $scope.logout = function() {
    AuthenticationService.logout().success(onLogoutSuccess);
  };
});
