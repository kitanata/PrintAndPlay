angular.module("app").controller('ContactController', function($scope, $location, AuthenticationService) {
  $scope.title = "Contact";
  $scope.message = "Mouse Over these images to see a directive at work";

  var onLogoutSuccess = function(response) {
    $location.path('/login');
  };

  $scope.logout = function() {
    AuthenticationService.logout().success(onLogoutSuccess);
  };
});
