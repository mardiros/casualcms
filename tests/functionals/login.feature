Feature: As a user, I can login

  Scenario: login with an incorrect password
    Given anonymous user on the admin page
    Then I see the login page
    When I fill the field "username" with "alice"
    And I fill the field "password" with "' or 1 = 1; --"
    And I click on the "Sign In" button
    Then I see the text "Bad username or password"
