import React from "react";
import { Routes, Route, Link } from "react-router-dom";
import { Box, Heading, Form, Button, Container, Tile } from "react-bulma-components";
import { Login } from "./ui/login/components"
import { PageNotFound } from "./ui/error404/components"


function Layout() {
  return (
    <>
      <Box>
        <Heading>
          <Link to="/admin/login">Sign In</Link>
        </Heading>
      </Box>
      <Container>
        <Routes>
          <Route path="login" element={<Login />} />
          <Route path="*" element={<PageNotFound />} />
        </Routes>
      </Container>
    </>
  )
}

function App() {
  return (
    <Routes>
      <Route path="admin/*" element={<Layout />} />
    </Routes>
  )
}


export { App };
